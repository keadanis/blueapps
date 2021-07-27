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
from odoo import api, fields, models


class SplitLead(models.Model):
    _name = 'split.lead'

    lead_id = fields.Many2one('crm.lead', ondelete='cascade', index=True)
    sequence = fields.Integer(
        string='Sequence', default=10,
        help="Gives the sequence of this line when displaying.")
    comercial_id = fields.Many2one(
        'res.users',
        string="Commercial",
        help="The commercial that participated in the opportunity")
    percentaje = fields.Float(
        string="Percentage",
        store=True,
        help="The percentage that the commercial won in this opportunity")
    amount_percent = fields.Float(
        string="Amount Percent",
        store=True,
        help="amount corresponding to the percentage according to the total of "
             "the opportunity")

    @api.onchange('percentaje')
    def compute_total_percent(self):
        for line in self:
            if line.percentaje and line.lead_id.expected_revenue:
                amount_percent = (float(line.percentaje) / 100) * float(
                    line.lead_id.expected_revenue)
                line.amount_percent = amount_percent

    @api.onchange('amount_percent')
    def compute_total_amount(self):
        for line in self:
            if line.amount_percent and line.lead_id.expected_revenue:
                total_percent = (
                    float(line.amount_percent) * 100) / (float(
                        line.lead_id.expected_revenue))
                line.percentaje = total_percent
