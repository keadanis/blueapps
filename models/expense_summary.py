# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools
from datetime import datetime , time
from odoo.tools.profiler import profile
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import os
import time

class ExpenseSummary(models.Model):
    _name = 'expense.summary'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Expense Summary'
    _order = 'date desc'
    
    name = fields.Char('Description',track_visibility="onchange")
    date = fields.Date('Date',track_visibility="onchange")
    amount = fields.Float('Expense Amount',track_visibility="onchange", copy=False)
    location = fields.Char('Location')
    exp_category_id = fields.Many2one('expense.category', string='Category',track_visibility="onchange")
    account_journal_id = fields.Many2one('bank.account', string='Account',track_visibility="onchange",auto_join=True,ondelete='cascade')
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    bill_ref = fields.Many2many('ir.attachment',string='Bill Refrence', attachment=True)
    description = fields.Text('Notes..')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.user.currency_id)
    
    
    