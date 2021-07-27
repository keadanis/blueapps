# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import date
from odoo import api, fields, models


class InvestmentInterest(models.Model):
    _name = 'investment.interest'
    _rec_name = 'bank_id' 
    
    date = fields.Date('Date', default=fields.Date.today, copy=False)
    amount = fields.Float('Current Amount',copy=False)
    bank_id = fields.Many2one('bank.account','Account')
    
    @api.model
    def create(self, vals):
        res = super(InvestmentInterest, self).create(vals) 
        today = fields.Date.context_today(self)
        bank = self.env['bank.account'].browse(vals['bank_id'])
        current_balance = bank.account_balance(bank, today)
        interest = vals['amount'] - current_balance
        category_id = self.env['income.category'].search([('name','=', 'Investment Interest')])
        self.env['income.summary'].create({
            'name': bank.name + ' Interest',
            'date': vals['date'],
            'amount': interest,
            'account_journal_id': bank.id,
            'income_categ_id': category_id.id,
            'investment_id': res.id
            })
        return res
    
    @api.multi
    def unlink(self):
        for interest in self:
            income_summary = self.env['income.summary'].search([('investment_id','=',self.id)])
            income_summary.unlink()
        return super(InvestmentInterest, self).unlink()
    
