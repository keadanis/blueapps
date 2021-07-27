
# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import date, datetime
from odoo.http import request, Response



class BankAccount(models.Model):
    _name = 'bank.account'


    name = fields.Char('Account Name', copy=False)
    type = fields.Selection([('investment','Investment'),
                             ('saving','Saving'),
                             ('checking','Checking'),
                             ('loan','Loan'),
                             ('credit', 'Credit Card')])
    yearly_opening_balance_ids = fields.One2many('bank.account.line', 'bank_id', 'Opening Balance')


    def amount_transfered(self, acct, start_date, last_day):
        debit_amount = amount_credited = 0
        request.env.cr.execute("""select sum(amount) from account_money_transfer where date >= %s  AND date <= %s
                             AND source_journal_id = %s
                            """,
                             ((start_date, last_day, acct.id)))
        amount_debited = request.env.cr.dictfetchall()
        request.env.cr.execute("""select sum(amount) from account_money_transfer where date >= %s  AND date <= %s
                             AND dest_journal_id = %s
                            """,
                             ((start_date, last_day, acct.id)))
        amount_credited = request.env.cr.dictfetchall()
        if amount_debited:
            debit_amount = amount_debited[0]['sum']
        if amount_credited:
            credit_amount = amount_credited[0]['sum']
        return debit_amount, credit_amount



    def account_balance(self, acct, last_day):
        start_date = date(last_day.year, 1, 1)
        debit, credit = self.amount_transfered(acct, start_date, last_day)
        account_line_id = request.env['bank.account.line'].sudo().search([('bank_id','=',acct.id),
                                                                          ('year','=',str(last_day.year))])
        request.env.cr.execute("""select sum(amount) from expense_summary where date >= %s AND date <= %s
                             AND account_journal_id = %s """,
                             ((start_date, last_day, acct.id)))
        total_exp = request.env.cr.dictfetchall()
        request.env.cr.execute("""select sum(amount) from income_summary where date >= %s AND date <= %s
                             AND account_journal_id = %s
                            """,
                             ((start_date, last_day, acct.id)))
        total_inc = request.env.cr.dictfetchall()
        if total_inc:
            total_income = total_inc[0]['sum'] or 0.0
        if total_exp:
            total_exp = total_exp[0]['sum'] or 0.0
        balance = (account_line_id.initial_balance + total_income) - total_exp
        if debit:
            balance -= debit
        if credit:
            balance += credit
        return balance



class BankAccountLine(models.Model):
    _name = 'bank.account.line'


    bank_id = fields.Many2one('bank.account', 'Bank')
    year = fields.Many2one('budget.year', 'Year')
    initial_balance = fields.Float('Initial Balance')


    def amount_transfered(self, acct, last_day):
        debit_amount = amount_credited = 0
        start_date = date(2021, 1, 1)
        self._cr.execute("""select sum(amount) from account_money_transfer where date >= %s  AND date <= %s
                             AND source_journal_id = %s
                            """,
                             ((start_date, last_day, acct.id)))
        amount_debited = self._cr.fetchall()
        self._cr.execute("""select sum(amount) from account_money_transfer where date >= %s  AND date <= %s
                             AND dest_journal_id = %s
                            """,
                             ((start_date, last_day, acct.id)))
        amount_credited = self._cr.fetchall()

        if amount_debited:
            debit_amount = amount_debited[0][0]
        if amount_credited:
            credit_amount = amount_credited[0][0]
        return debit_amount, credit_amount

    def account_balance(self, acct, last_day):

        debit, credit = self.amount_transfered(acct, last_day)
        start_date = date(last_day.year, 1, 1)
        account_line_id = self.env['bank.account.line'].sudo().search([('bank_id','=',acct.id),
                                                                          ('year','=',str(last_day.year))])
        self._cr.execute("""select sum(amount) from expense_summary where date >= %s AND date <= %s
                             AND account_journal_id = %s
                            """,
                             ((start_date, last_day, acct.id)))
        total_exp = self._cr.fetchall()
        self._cr.execute("""select sum(amount) from income_summary where date >= %s AND date <= %s
                             AND account_journal_id = %s
                           """,
                             ((start_date, last_day, acct.id)))

        total_inc = self.env.cr.fetchall()
        if total_inc:
            total_income = total_inc[0][0] or 0.0
        if total_exp:
            total_exp = total_exp[0][0] or 0.0
        balance = (account_line_id.initial_balance  + total_income ) - (total_exp)
        if debit:
            balance -= debit
        if credit:
            balance += credit
        return balance

    @api.model
    def _cron_create_opening_balance(self):
        today = datetime.today()
        last_day = date(today.year-1 , 12, 31)
        year = self.env['budget.year'].search([('name','=', today.year)])

        accounts = self.env['bank.account'].search([])
        for account in accounts:
            current_opening_balance = self.search([('bank_id','=', account.id),('year','=', year.id)])
            if not current_opening_balance:
                self.create({
                    'bank_id': account.id,
                    'year': year.id,
                    'initial_balance' : self.account_balance(account,last_day)
                    })

class BudgetYear(models.Model):
    _name = 'budget.year'
    name = fields.Char('Year', copy=False)
