# -*- encoding: utf-8 -*-
#
# Module written to Odoo, Open Source Management Solution
#
# Copyright (c) 2021 Wedoo - https://wedoo.tech/
# All Rights Reserved.
#
# Developer(s): Alan Guzmán
#               (age@wedoo.tech)
########################################################################
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
########################################################################
from odoo import api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'


    def _create_invoices(self, grouped=False, final=False):
        res = super(SaleOrder, self)._create_invoices(
            grouped=grouped, final=final
        )
        for order in self:
            if order.opportunity_id:
                sale_ids = self.env['sale.order'].search([
                    ('opportunity_id', '=', order.opportunity_id.id),
                    ('state', 'in', ('sale', 'done'))])
                invoice_ids = sale_ids.invoice_ids.filtered(
                    lambda x: x.state != 'cancel' and x.move_type == 'out_invoice')
                if invoice_ids:
                    amount = max(invoice_ids.mapped('amount_total'))
                    order.opportunity_id.expected_revenue = amount
        return res
