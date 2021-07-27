# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class AccountMoneyTransfer(models.Model):
    _name = 'account.money.transfer'


    name = fields.Char('Note', copy=False)
    date = fields.Date('Date',copy=False)
    amount = fields.Float('Amount',copy=False)
    source_journal_id = fields.Many2one('bank.account','Source Account')
    dest_journal_id = fields.Many2one('bank.account','Destination Account')


class Users(models.Model):
    _inherit = 'res.users'
    currency_id = fields.Many2one('res.currency', string='Currency')