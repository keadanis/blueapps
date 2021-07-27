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
from datetime import timedelta, datetime, date, time, timezone
import pytz

import logging

_logger = logging.getLogger(__name__)

class RockerCompany(models.Model):
    _name = 'rocker.company.defaults'
    _description = 'Rocker Company Defaults'
    _sql_constraints = [
        ('unique_defaults', 'unique (company_id)', 'Only one defaults per company!')
    ]

    company_id = fields.Many2one('res.company', "Company", default=lambda self: self.env.company, store=True)
    company_name = fields.Char('Company', store=False, required=False, related='company_id.name')
    rocker_default_start = fields.Float('Default Start Time [UTC]', store=True, readonly=False, help="Office start time")
    rocker_default_stop = fields.Float('Default Stop Time [UTC]', store=True, readonly=False, help="Office end time")
    rocker_default_work = fields.Float('Default Work amount', store=True, readonly=False, help="Work does not contain breaks like lunch hour")
    rocker_default_startToShow = fields.Float('Default Start Time [Local]', compute='_compute_show_start', store=False, readonly=False, help="Office start time")
    rocker_default_stopToShow = fields.Float('Default Stop Time [Local]', compute='_compute_show_stop', store=False, readonly=False, help="Office end time")

    @api.onchange('rocker_default_startToShow')
    def _onchange_rocker_default_startToShow(self):
        self.ensure_one()
        self.rocker_default_start = self.to_UTC(self.rocker_default_startToShow)

    @api.onchange('rocker_default_stopToShow')
    def _onchange_rocker_default_stopToShow(self):
        self.ensure_one()
        self.rocker_default_stop = self.to_UTC(self.rocker_default_stopToShow)

    @api.depends('rocker_default_startToShow')
    def _compute_show_start(self):
        _logger.debug('company compute_show_start')
        self.ensure_one()
        self.rocker_default_startToShow = self.to_LOCAL(self.rocker_default_start)

    @api.depends('rocker_default_stopToShow')
    def _compute_show_stop(self):
        _logger.debug('company compute_show_stop')
        self.ensure_one()
        self.rocker_default_stopToShow = self.to_LOCAL(self.rocker_default_stop)

    def to_UTC(self, dt):
        user = self.env.user
        if user.tz:
            tz = pytz.timezone(user.tz) or pytz.utc
            usertime = pytz.utc.localize(datetime.now()).astimezone(tz)
            offset = tz.utcoffset(datetime.now())
        else:
            tz = pytz.timezone('UTC')
            usertime = pytz.utc.localize(datetime.now()).astimezone(tz)
            offset = tz.utcoffset(datetime.now())

        return dt - offset.total_seconds() / 3600

    def to_LOCAL(self, dt):
        user = self.env.user
        if user.tz:
            tz = pytz.timezone(user.tz) or pytz.utc
            usertime = pytz.utc.localize(datetime.now()).astimezone(tz)
            offset = tz.utcoffset(datetime.now())
        else:
            tz = pytz.timezone('UTC')
            usertime = pytz.utc.localize(datetime.now()).astimezone(tz)
            offset = tz.utcoffset(datetime.now())

        return dt + offset.total_seconds() / 3600

    @api.model
    def edit_rocker_company_defaults(self):
        _default_id = self.env['rocker.company.defaults'].search([('company_id','=',self.env.company.id)]).id
        if _default_id:
            return {
                'name': 'Edit Company Defaults',
                'res_model':'rocker.company.defaults',
                'view_mode':'form',
                'res_id':_default_id,
                'type':'ir.actions.act_window',
                'view_type':'form',
                'view_id':self.env.ref('rocker_timesheet.rocker_company_view_form_simplified').id,
                'target':'new',
            }
        else:
            return {
                'name': 'Create Company Defaults',
                'res_model':'rocker.company.defaults',
                'view_mode':'form',
                # 'res_id':_default_id,
                'type':'ir.actions.act_window',
                'view_type':'form',
                'view_id':self.env.ref('rocker_timesheet.rocker_company_view_form_simplified').id,
                'target':'new',
            }


class RockerUser(models.Model):
    _name = 'rocker.user.defaults'
    _description = 'Rocker User Defaults to Rocker Timesheet'
    _sql_constraints = [
        ('unique_defaults', 'unique (user_id,company_id)', 'Only one defaults per user per company!')
    ]
    user_id = fields.Many2one('res.users', string='User', index=True, default=lambda self: self.env.user, store=True)
    user_name = fields.Char('User', store=False, required=False, related='user_id.name')
    company_id = fields.Many2one('res.company', "Company", default=lambda self: self.env.company, store=True)
    employee_id = fields.Many2one('hr.employee', "Employee",
                                  default=lambda self: self.env['hr.employee'].search([('user_id', '=', self.env.user.id), ('company_id','=',self.env.company.id)]).id, store=True)
    department_id = fields.Many2one('hr.department', "Department", compute='_compute_department_id', store=True, compute_sudo=True)

    rocker_default_start = fields.Float('Default Start Time [UTC]', store=True, readonly=False, help="Office start time")
    rocker_default_stop = fields.Float('Default Stop Time [UTC]', store=True, readonly=False, help="Office end time")
    rocker_default_work = fields.Float('Default Work amount', store=True, readonly=False, help="Work does not contain breaks like lunch hour")
    rocker_default_startToShow = fields.Float('Default Start Time [Local]', compute='_compute_show_start', store=False, readonly=False, help="Office start time")
    rocker_default_stopToShow = fields.Float('Default Stop Time [Local]', compute='_compute_show_stop', store=False, readonly=False, help="Office end time")

    @api.depends('employee_id')
    def _compute_department_id(self):
        self.ensure_one()
        self.department_id = self.employee_id.department_id

    @api.onchange('rocker_default_startToShow')
    def _onchange_rocker_default_startToShow(self):
        self.ensure_one()
        self.rocker_default_start = self.to_UTC(self.rocker_default_startToShow)

    @api.onchange('rocker_default_stopToShow')
    def _onchange_rocker_default_stopToShow(self):
        self.ensure_one()
        self.rocker_default_stop = self.to_UTC(self.rocker_default_stopToShow)

    @api.depends('rocker_default_startToShow')
    def _compute_show_start(self):
        _logger.debug('company compute_show_start')
        self.ensure_one()
        self.rocker_default_startToShow = self.to_LOCAL(self.rocker_default_start)

    @api.depends('rocker_default_stopToShow')
    def _compute_show_stop(self):
        _logger.debug('company compute_show_stop')
        self.ensure_one()
        self.rocker_default_stopToShow = self.to_LOCAL(self.rocker_default_stop)

    def to_UTC(self, dt):
        user = self.env.user
        if user.tz:
            tz = pytz.timezone(user.tz) or pytz.utc
            usertime = pytz.utc.localize(datetime.now()).astimezone(tz)
            offset = tz.utcoffset(datetime.now())
        else:
            tz = pytz.timezone('UTC')
            usertime = pytz.utc.localize(datetime.now()).astimezone(tz)
            offset = tz.utcoffset(datetime.now())

        return dt - offset.total_seconds() / 3600

    def to_LOCAL(self, dt):
        user = self.env.user
        if user.tz:
            tz = pytz.timezone(user.tz) or pytz.utc
            usertime = pytz.utc.localize(datetime.now()).astimezone(tz)
            offset = tz.utcoffset(datetime.now())
        else:
            tz = pytz.timezone('UTC')
            usertime = pytz.utc.localize(datetime.now()).astimezone(tz)
            offset = tz.utcoffset(datetime.now())

        return dt + offset.total_seconds() / 3600

    @api.model
    def edit_rocker_user_defaults(self):
        _default_id = self.env['rocker.user.defaults'].search([('user_id', '=', self.env.user.id), ('company_id','=',self.env.company.id)]).id
        if _default_id:
            return {
                'name': 'Edit User defaults',
                'res_model':'rocker.user.defaults',
                'view_mode':'form',
                'res_id':_default_id,
                'type':'ir.actions.act_window',
                'view_type':'form',
                'view_id':self.env.ref('rocker_timesheet.rocker_user_view_form_simplified').id,
                'target':'new',
            }
        else:
            return {
                'name': 'Create User defaults',
                'res_model':'rocker.user.defaults',
                'view_mode':'form',
                # 'res_id':self._default_id,
                'type':'ir.actions.act_window',
                'view_type':'form',
                'view_id':self.env.ref('rocker_timesheet.rocker_user_view_form_simplified').id,
                'target':'new',
            }

