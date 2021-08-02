# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api

class AccountInvoice(models.Model):
    _inherit = "account.move"
    _description = "Account Invoice Paid Amounts"

    paid_amount = fields.Monetary(string='Paid Amount', compute='_compute_paid_amount', store=True, help="The Paid Amount.")

    @api.depends('amount_residual')
    def _compute_paid_amount(self):
        for inv in self:
            inv.paid_amount = 0.0
            if inv.state != 'draft':
                inv.paid_amount = inv.amount_total - inv.amount_residual
