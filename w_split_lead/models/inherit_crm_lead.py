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
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    split_lead_ids = fields.One2many(
        'split.lead', 'lead_id')
    show_split = fields.Boolean(default=False)
    show_note = fields.Boolean(default=False)

    @api.onchange('split_lead_ids')
    def onchange_split_lines(self):
        total_percent = 0
        if len(self.split_lead_ids) > 0:
            total_percent = sum(
                [line.percentaje for line in self.split_lead_ids])
        if self.show_split is False:
            self.show_note = False
        else:
            if total_percent < 100 or total_percent > 100:
                self.show_note = True
            else:
                self.show_note = False

    def write(self, vals):
        split_obj = self.env['split.lead']
        res = super(CrmLead, self).write(vals)
        if (vals.get('probability') == 100 or self.probability == 100) and (
                vals.get('show_split') is False or self.show_split is False):
            self.write({'show_split': True})
            amount_percent = (
                (vals.get(
                    'expected_revenue') or self.expected_revenue) / 100) * float(
                (vals.get('probability') or self.probability))
            values = {
                'lead_id': self.id,
                'comercial_id': self.user_id.id,
                'percentaje': (float(vals.get(
                    'probability', False)) or self.probability),
                'amount_percent': amount_percent or 0.0
            }
            split_obj.create(values)
        if vals.get('expected_revenue') and self.show_split is True:
            for line in self.split_lead_ids:
                amount_percent = (float(line.percentaje) / 100) * float(
                    vals.get('expected_revenue'))
                line.amount_percent = amount_percent

        if vals.get('show_note') is True:
            raise UserError(_(
                'The total amount of the splits lines must be equal to '
                'the probability percent of the opportunity!'))
        return res
