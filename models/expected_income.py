# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _
from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta
import babel
from odoo.exceptions import  ValidationError

class ExpectedIncome(models.Model):
    _name = 'expected.income'
    
    
    def _default_line_ids(self):
        inc_categ_list = []
        inc_categ_ids = self.env['income.category'].search([('show_default','=', True)])
        for categ in inc_categ_ids:
            inc_categ_list.append((0, 0, {'category_id':categ.id,
                                          'currency_id':self.env.user.company_id.currency_id}))
        return inc_categ_list
    
    @api.depends('exp_income_ids.line_amount')
    def _amount_total(self):
        for income in self:
            tot = 0
            for line in income.exp_income_ids:
                tot += line.line_amount
            income.amount_total = tot
        
    name = fields.Char('Name',  copy=False, index=True)
    date_from = fields.Date(string='Date From',  required=True,
        default=lambda self: fields.Date.to_string(date.today().replace(day=1)))
    date_to = fields.Date(string='Date To',  required=True,
        default=lambda self: fields.Date.to_string((datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()),
        )
    exp_income_ids = fields.One2many('expected.income.line', 'exp_income_id', string="Expected Income", copy=True,store=True, default=_default_line_ids)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.user.currency_id)
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_total')


    @api.onchange('date_from', 'date_to')
    def onchange_date(self):       
        date_from = self.date_from
        date_to = self.date_to
        ttyme = datetime.combine(fields.Date.from_string(date_from), time.min)
        locale = self.env.context.get('lang') or 'en_US'
        self.name = _('Expected Income for %s') % (tools.ustr(babel.dates.format_date(date=ttyme, format='MMMM-y', locale=locale)))
    
    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        if self.date_from > self.date_to:            
            raise ValidationError(_("'Date From' must be earlier 'Date To'.")) 
    
    
class ExpectedIncomeLine(models.Model):
    _name = 'expected.income.line'
    _rec_name = 'category_id'
    
  
    exp_income_id = fields.Many2one('expected.income', string='Expected income')
    category_id = fields.Many2one('income.category', string='Category')    
    line_amount = fields.Monetary(string='Amount', store=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.user.currency_id)

    
    
class IncomeCategory(models.Model):
    _name = 'income.category'
    
    name = fields.Char('Income Category')
    show_default = fields.Boolean('Show Default', default=True)

    