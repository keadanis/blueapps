# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _
from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta
import babel
from odoo.exceptions import  ValidationError


class BudgetedExpense(models.Model):
    _name = 'budgeted.expense'
    
    def _default_line_ids(self):
        exp_categ_list = []
        exp_categ_ids = self.env['expense.category'].search([('show_default','=', True)])
        for categ in exp_categ_ids:
            exp_categ_list.append((0, 0, {'category_id':categ.id,
                                          'currency_id':self.env.user.company_id.currency_id}))
        return exp_categ_list
    
    @api.depends('budget_expense_ids.amount')
    def _amount_total(self):
        for budget in self:
            tot = 0
            for line in budget.budget_expense_ids:
                tot += line.amount
            budget.amount_total = tot
            
    name = fields.Char('Name',  copy=False, index=True)
    date_from = fields.Date(string='Date From',  required=True,
        default=lambda self: fields.Date.to_string(date.today().replace(day=1)))
    date_to = fields.Date(string='Date To',  required=True,
        default=lambda self: fields.Date.to_string((datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()),
        )
    budget_expense_ids = fields.One2many('budget.expense.lines', 'budgeted_id', string="Budgeted Expenses", copy=True,store=True, default=_default_line_ids)
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_total')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.user.currency_id)

    @api.onchange('date_from', 'date_to')
    def onchange_date(self):       
        date_from = self.date_from
        date_to = self.date_to

        ttyme = datetime.combine(fields.Date.from_string(date_from), time.min)
        locale = self.env.context.get('lang') or 'en_US'
        self.name = _('Budgeted Expenses for %s') % (tools.ustr(babel.dates.format_date(date=ttyme, format='MMMM-y', locale=locale)))
    
    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        if self.date_from > self.date_to:            
            raise ValidationError(_("'Date From' must be earlier 'Date To'."))  
    
class BudgetExpenseLines(models.Model):
    _name = 'budget.expense.lines'
    _rec_name = 'budgeted_id'

    budgeted_id = fields.Many2one('budgeted.expense', string='Budget')
    category_id = fields.Many2one('expense.category', string='Category')
    amount = fields.Monetary(string='Amount', store=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.user.currency_id)
    
    
class ExpenseCategory(models.Model):
    _name = 'expense.category'
    
    name = fields.Char('Expense Category')
    show_default = fields.Boolean('Show Default', default=True)