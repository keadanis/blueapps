# -*- coding: utf-8 -*-
#################################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2021-Today Ascetic Business Solution <www.asceticbs.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################
from odoo import api,fields,models,_

class SaveFilter(models.Model):
    _name = "save.filter"
    _description = 'Save Filter'
    _rec_name = 'filer_name'

    filer_name = fields.Char(string="Name")
    salesperson_ids = fields.Many2many('res.users', string="Salesperson")
    team_ids = fields.Many2many(comodel_name='crm.team',relation='trial_table1',column1='trial_id1',column2='trial_name1',  string="Sales Team")
    not_team_ids = fields.Many2many('crm.team', string="Sales Team Not Set")
    tags_ids = fields.Many2many(comodel_name='crm.tag',relation='trial_table2',column1='trial_id2',column2='trial_name2', string='Tags')
    not_tags_ids = fields.Many2many('crm.tag', string="Tags Not Set")
