# -*- coding: utf-8 -*-
#################################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2021-today Ascetic Business Solution <www.asceticbs.com>
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
from odoo import fields,api,models,_
from odoo.exceptions import ValidationError

class SearchSalesperson(models.TransientModel):
    _name = 'search.salesperson'
    _description = 'Search Salesperson Lead & Opportunity'

    salesperson_ids = fields.Many2many('res.users', string="Salesperson")
    filter_id = fields.Many2one('save.filter', string="Filter")
    team_ids = fields.Many2many(comodel_name='crm.team',relation='trial_1',column1='trial_id_1',column2='trial_name_1',  string="Sales Team")
    not_team_ids = fields.Many2many('crm.team', string="Sales Team Not Set")
    tags_ids = fields.Many2many(comodel_name='crm.tag',relation='trial_2',column1='trial_id_2',column2='trial_name_2', string='Tags')
    not_tags_ids = fields.Many2many('crm.tag', string="Tags Not Set")
    save_filter = fields.Boolean(string='Save Filter')
    filer_name = fields.Char(string="Filter Name")

    @api.onchange('filter_id')
    def onchange_filter_id(self):
        if self.filter_id:
            self.salesperson_ids = self.filter_id.salesperson_ids
            self.team_ids = self.filter_id.team_ids
            self.not_team_ids = self.filter_id.not_team_ids
            self.tags_ids = self.filter_id.tags_ids
            self.not_tags_ids = self.filter_id.not_tags_ids

    def button_save_filter(self):
        share_vote = self.env['save.filter'].create({'filer_name' : self.filer_name,
                                                     'salesperson_ids' : self.salesperson_ids.ids,
                                                     'team_ids' : self.team_ids.ids,
                                                     'not_team_ids' : self.not_team_ids.ids,
                                                     'tags_ids' : self.tags_ids.ids,
                                                     'not_tags_ids' : self.not_tags_ids.ids,})
    def opportunity_lead(self):
        salesperson_list = []
        domain = []
        customer_ids = self.env['res.partner'].search([('user_id','in',self.salesperson_ids.ids)])
        for customer_id in customer_ids:
            salesperson_list.append(customer_id.id)
        if salesperson_list:
            domain.append(('partner_id', 'in',salesperson_list))
        if self.team_ids.ids:
            domain.append(('team_id', 'in',self.team_ids.ids))
        if self.not_team_ids.ids:
            domain.append(('team_id', 'not in',self.not_team_ids.ids))
        if self.tags_ids.ids:
            domain.append(('tag_ids', 'in',self.tags_ids.ids))
        if self.not_tags_ids.ids:
            domain.append(('tag_ids', 'not in',self.not_tags_ids.ids))
        return domain
               
    def search_opportunity(self):
        domain = []
        if not self.salesperson_ids and not self.team_ids and not self.not_team_ids and not self.tags_ids and not self.not_tags_ids:
            raise ValidationError("Data not found!") 
        else :
            domain = self.opportunity_lead()
            domain.append(('type', '=', 'opportunity'))
        opportunity_ids = self.env['crm.lead'].search(domain)
        return {
               'type': 'ir.actions.act_window',
               'name': 'Pipeline',
               'view_mode': 'tree,form',
               'res_model': 'crm.lead',
               'domain': domain,
               }

    def search_lead(self):
        domain = []
        if not self.salesperson_ids and not self.team_ids and not self.not_team_ids and not self.tags_ids and not self.not_tags_ids:
            raise ValidationError("Data not found!") 
        else :
            domain = self.opportunity_lead()
            domain.append(('type', '=', 'lead'))
        opportunity_ids = self.env['crm.lead'].search(domain)
        return {
               'type': 'ir.actions.act_window',
               'name': 'Lead',
               'view_mode': 'tree,form',
               'res_model': 'crm.lead',
               'domain': domain,
               }

    def search_opportunity_and_lead(self):
        if not self.salesperson_ids and not self.team_ids and not self.not_team_ids and not self.tags_ids and not self.not_tags_ids:
            raise ValidationError("Data not found!") 
        else :
            domain = self.opportunity_lead()
            domain.append(('type', 'in', ('opportunity', 'lead')))
        opportunity_ids = self.env['crm.lead'].search(domain)
        return {
               'type': 'ir.actions.act_window',
               'name': 'Lead',
               'view_mode': 'tree,form',
               'res_model': 'crm.lead',
               'domain': domain,
               }
