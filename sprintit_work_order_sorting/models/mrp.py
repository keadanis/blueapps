# -*- coding: utf-8 -*-
##############################################################################
#
#    ODOO Open Source Management Solution
#
#    ODOO Addon module by Sprintit Ltd
#    Copyright (C) 2020 Sprintit Ltd (<http://sprintit.fi>).
#
##############################################################################

from odoo import fields, models

class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'
    _order = "mrp_deadline_start_date"

    mrp_deadline_start_date = fields.Datetime(string='MRP Deadline Start', store=True, related='production_id.date_planned_start')
    kanban_color = fields.Char(string="Kanban Color", compute="_compute_kanban_color")

    def _compute_kanban_color(self):
        for rec in self:
            deadline_week = fields.Date.from_string(rec.mrp_deadline_start_date).isocalendar()[1]
            current_week = fields.Date.from_string(fields.Date.today()).isocalendar()[1] 
            if deadline_week == current_week:
                rec.kanban_color = '#88ce96'
            elif deadline_week < current_week:
                rec.kanban_color = '#f48b8b'
            else:
                rec.kanban_color = 'white'
