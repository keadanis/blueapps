# -*- coding: utf-8 -*-
###########################################################################
#
#    @author Xpath Solutions <xpathsolution@gmail.com>
#
###########################################################################
from odoo import models, api, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for order in self:
            order._create_invoices()
            for invoice in self.invoice_ids:
                invoice.action_post()
        return res
