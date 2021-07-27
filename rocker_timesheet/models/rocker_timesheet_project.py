# -*- coding: utf-8 -*-
#############################################################################
#
#    Copyright (C) 2021-Antti Kärki.
#    Author: Antti Kärki.
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError, Warning
from odoo import tools
from datetime import timedelta, datetime, date, time, timezone
import pytz

import logging

_logger = logging.getLogger(__name__)

class RockerTask(models.Model):
    _name = 'rocker.task'
    _auto = False
    _description = 'values from database'

    @api.model
    def _domain_project_id(self):
        domain = [('allow_timesheets', '=', True)]
        if not self.user_has_groups('hr_timesheet.group_timesheet_manager'):
            return expression.AND([domain,
                                   ['|', ('project_id.privacy_visibility', '!=', 'followers'), ('project_id.allowed_internal_user_ids', 'in', self.env.user.ids)]
                                   ])
        return domain

    id = fields.Integer('id')
    name = fields.Char('Name')
    company_id = fields.Many2one('res.company', string='Company', domain="[('company_id', '=', self.env.company.id)]")
    project_id = fields.Many2one('project.project', domain=_domain_project_id)
    task_id = fields.Many2one('project.task', string='Task')
    parent_id = fields.Many2one('rocker.task', string='Parent')
    user_id = fields.Many2one('res.users', string='User')
    allow_timesheets = fields.Boolean("Allow Timesheets")
    privacy_visibility = fields.Char("Privacy Visibility")
    level = fields.Integer("Level")
    allowed_internal_user_ids = fields.Many2many('res.users', 'project_allowed_internal_users_rel','project_project_id','res_users_id',
                                                 string="Allowed Internal Users")


    @api.model
    def init(self):
        _logger.debug('Init: create view')
        tools.drop_view_if_exists(self.env.cr, self._table)
        # self._cr.execute("""DROP VIEW IF EXISTS ROCKER_TASK""")
        # id when taken from project_id can not be the same number than task_id, convert project_id to negative
        self.env.cr.execute("""
                    CREATE VIEW rocker_task AS
                    WITH RECURSIVE ctename AS (
                        SELECT t1.id as id, t1.name as name, t1.company_id as company_id, t1.project_id as project_id, 
                                 t1.id as task_id, -1 * project_id as parent_id, t1.user_id as user_id,
                                 1 as level
                        FROM project_task t1
						WHERE parent_id is null and active = TRUE
                    UNION ALL
                        SELECT t2.id, t2.name, t2.company_id as company_id, t2.project_id as project_id,
                             t2.id as task_id, t2.parent_id as parent_id, t2.user_id as user_id,
                             ctename.level + 1
                        FROM project_task t2
                         JOIN ctename ON t2.parent_id = ctename.id
                         WHERE active = TRUE
                    )
                    SELECT ct.id, ct.name, ct.project_id, ct.task_id, ct.parent_id, ct.user_id,
					    p.company_id, p.privacy_visibility, p.allow_timesheets, ct.level
                    FROM ctename ct
					JOIN project_project p ON p.id = ct.project_id  
                    WHERE p.allow_timesheets = TRUE
                    AND p.active = TRUE
					UNION ALL
					SELECT -1 * p1.id as id, p1.name as name, p1.id as project_id, null as task_id, null as parent_id, p1.user_id, 
					    p1.company_id, p1.privacy_visibility, p1.allow_timesheets,
                                 0 AS level
                    FROM project_project p1
                    WHERE p1.allow_timesheets = TRUE 
                    AND p1.active = TRUE
                    AND p1.id IN (SELECT project_id FROM project_task t3 
								  WHERE t3.active = TRUE)
                    """)

class RockerProject(models.Model):
    _inherit = 'project.project'
    _name = 'project.project'
    _description = 'Rocker Project'
    _order = 'sequence, id'

    rocker_type = fields.Selection([
        ('internal', 'Internal'),
        ('billable', 'Billable'),
        ('nonbillable', 'Non Billable')], 'Type', required=False, default='')

    def open_project(self, context=None):
        view_id = self.env.ref('rocker_timesheet.rocker_edit_project').id
        context = self._context.copy()
        return {
            'name': 'Project',
            'res_model':'project.project',
            'view_mode':'form',
            'res_id':self.id,
            'type':'ir.actions.act_window',
            'view_type':'form',
            'view_id':view_id,
            'target':'new',
        }
