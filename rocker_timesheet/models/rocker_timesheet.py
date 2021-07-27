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
from dateutil.rrule import rrule, DAILY
from odoo.osv import expression
import pytz

import logging

_logger = logging.getLogger(__name__)
default_start_time = 9
default_end_time = 16.5
default_duration = 7.5
default_unit_amount = 7.5
project_change = True
user_values = [(0,0,'filter')]
daystocreate = 0
prev_company = -1


class RockerTimesheet(models.Model):
    _inherit = 'account.analytic.line'
    _name = 'account.analytic.line'
    # _name = 'rocker.timesheet'
    # _description = 'Rocker Timesheet'
    _order = "date desc"


    @api.model
    def _default_user(self):
        _logger.debug('_default_user')
        return self.env.context.get('user_id', self.env.user.id)

    def _domain_project_id(self):
        domain = [('allow_timesheets', '=', True)]
        return expression.AND([domain,
                               ['|', ('privacy_visibility', '!=', 'followers'), ('allowed_internal_user_ids', 'in', self.env.user.ids)]
                               ])
        return domain

    def _domain_project_id_search(self):
        domain = [('company_id', '=', self.env.company.id)]
        return domain

    def _set_search_id(self, id):
        _i = 0
        _bfound = False
        _i = int(self.env.user.id)
        _logger.debug('user_values _i = ' + str(_i))
        _logger.debug('user_values id = ' + str(id))
        if id < 1:  # id < 1 when project row selected
            return False
        _logger.debug('user_values _i = ' + str(_i))
        _logger.debug('user_values = ' + str(user_values))
        for i in range(len(user_values)):
            if user_values[i][0] == _i:
                # user_values[i][0] = _i    # user_id
                user_values[i][1] = id      # selected task_id
                _bfound = True
        if not _bfound:
            values1 = [_i, id,'']
            user_values.append(values1)
        _logger.debug('user_values' + str(user_values))
        return True

    def _get_search_id(self):
        _i = 0
        _selected_id = 0
        _bfound = False
        _i = int(self.env.user.id)
        _logger.debug('user_values _i = ' + str(_i))
        _logger.debug('user_values = ' + str(user_values))
        for i in range(len(user_values)):
            if user_values[i][0] == _i:
                _selected_id = user_values[i][1]
                _bfound = True
        if not _bfound:
            _logger.debug('Selected id not found')
            return -1
        _logger.debug('Returning Selected id: ' + str(_selected_id))
        return _selected_id

    def _domain_get_search_filter(self):
        _i = 0
        _filt = ""
        _bfound = False
        _i = int(self.env.user.id)
        for i in range(len(user_values)):
            if user_values[i][0] == _i:
                # user_values[i][0] = _i
                _filt = user_values[i][2]
                _bfound = True
        if not _bfound:
            _logger.debug('filter not found')
            return ""
        _logger.debug('Returning _search_panel_filter: ' + str(_filt))
        return _filt

    def _domain_set_search_filter(self, filt):
        _i = 0
        _bfound = False
        _i = int(self.env.user.id)
        for i in range(len(user_values)):
            if user_values[i][0] == _i:
                user_values[i][2] = filt
                _bfound = True
        if not _bfound:
            values1 = [_i, 0, filt]
            user_values.append(values1)
        return True

    def _domain_get_search_domain(self, filt):
        # default = all
        _search_panel_domain = [('company_id', '=', self.env.company.id)]  # ok
        if filt == 'all':
            _search_panel_domain = _search_panel_domain + []
        elif filt == 'member':
            _search_panel_domain = _search_panel_domain + [('project_id', 'in', self.env['project.project'].search([('allowed_internal_user_ids', 'in', self.env.user.ids)]).ids)]
        elif filt == 'internal':
            _search_panel_domain = _search_panel_domain + [('project_id', 'in', self.env['project.project'].search([('rocker_type', '=', 'internal')]).ids)]
        elif filt == 'billable':
            _search_panel_domain = _search_panel_domain + [('project_id', 'in', self.env['project.project'].search([('rocker_type', '=', 'billable')]).ids)]
        elif filt == 'nonbillable':
            _search_panel_domain = _search_panel_domain + [('project_id', 'in', self.env['project.project'].search([('rocker_type', '=', 'nonbillable')]).ids)]
        elif filt == 'mine':
            _search_panel_domain = _search_panel_domain + \
                        ['|',
                            ('task_id', 'in', self.env['project.task'].search([('user_id', '=', self.env.user.id)]).ids),
                          '&',  ('task_id', '=', False),
                                ('project_id', 'in', self.env['project.task'].search([('user_id', '=', self.env.user.id)]).project_id.ids),
                         ]
        else:
            self._domain_get_search_domain('all')
        _search_panel_domain = expression.AND([_search_panel_domain,
                   ['|', ('privacy_visibility', '!=', 'followers'), ('project_id.allowed_internal_user_ids', 'in', self.env.user.ids)]
                   ])
        _logger.debug('Search Panel domain set to: ' + str(_search_panel_domain))
        return _search_panel_domain

    def _domain_employee_id(self):
        return [('user_id', '=', self.env.user.id)]

    def _get_defaults(self):
        _logger.debug('get defaults')
        global default_start_time
        global default_end_time
        global default_duration
        global default_unit_amount
        _defaults = None
        _defaults = self.env['rocker.user.defaults'].search([('user_id', '=', self.env.user.id), ('company_id','=',self.env.company.id)]) \
            or self.env['rocker.company.defaults'].search([('company_id','=',self.env.company.id)])
        if _defaults:
            _logger.debug('defaults start set to: ' + str(_defaults.rocker_default_start))
            default_start_time = _defaults.rocker_default_start
            default_end_time = _defaults.rocker_default_stop
            default_duration = _defaults.rocker_default_stop - _defaults.rocker_default_start
            default_unit_amount = _defaults.rocker_default_work
        else:
            _logger.debug('No defaults, create company defaults')
            _user = self.env.user
            if _user.tz:
                tz = pytz.timezone(_user.tz) or pytz.utc
            else:
                tz = pytz.timezone('UTC')
            _offset = tz.utcoffset(datetime.now())
            _hourdiff = int(_offset.total_seconds()/3600)
            _start = 9 - _hourdiff
            _end = 17 - _hourdiff
            self.env['rocker.company.defaults'].sudo().create({
                'company_id': self.env.company.id,
                'rocker_default_start': _start,
                'rocker_default_stop': _end,
                'rocker_default_work': 7.5
            })
            self._get_defaults()
        return True

    def _default_start(self):
        _logger.debug('_default_start')
        self._get_defaults()
        return (fields.Date.today() + timedelta(hours=default_start_time)).strftime('%Y-%m-%d %H:%M')

    def _default_date(self):
        _logger.debug('_default_date')
        return fields.Date.today()

    def _default_stop(self):
        _logger.debug('_default_stop')
        # self._get_defaults()
        return (fields.Date.today() + timedelta(hours=default_end_time)).strftime('%Y-%m-%d %H:%M')

    def _default_start_time(self):
        _logger.debug('_default_start_time')
        self._get_defaults()
        return default_start_time

    def _default_end_time(self):
        _logger.debug('_default_end_time')
        # self._get_defaults()
        return default_end_time

    def _default_duration(self):
        _logger.debug('_default_duration')
        self._get_defaults()
        return default_duration

    def _default_work(self):
        _logger.debug('_default_work: ' + str(default_unit_amount))
        # self._get_defaults()
        return default_unit_amount

    def _get_duration(self, start, stop):
        _logger.debug('_get_duration')
        if not start or not stop:
            return 0
        duration = (stop - start).total_seconds() / 3600
        return round(duration, 2)

    def _default_name(self):
        _logger.debug('_default_name')
        _selected_id = 0
        _selected_id = self._get_search_id()
        if _selected_id > 0:
            search_task = self.env['project.task'].search([('id', '=', _selected_id)], limit=1)
            if search_task.id > 0:
                return str(search_task.name)
        else:
            return None

    def _default_task(self):
        _logger.debug('_default_task')
        _selected_id = 0
        _selected_id = self._get_search_id()
        if _selected_id > 0:
            search_task = self.env['project.task'].search([('id', '=', _selected_id)], limit=1)
            if search_task.id > 0:
                return search_task.id
        return None

    def _default_project(self):
        _logger.debug('_default_project')
        _selected_id = 0
        _selected_id = self._get_search_id()
        if _selected_id > 0:
            search_task = self.env['project.task'].search([('id', '=', _selected_id)], limit=1)
            if search_task.id > 0:
                return search_task.project_id
        return None



    # existing fields
    company_id = fields.Many2one('res.company', "Company", default=lambda self: self.env.company, store=True, required=True)
    task_id = fields.Many2one(
        'project.task', 'Task', compute='_compute_task_id', store=True, readonly=False, index=True,
        domain="[('company_id', '=', company_id), ('project_id.allow_timesheets', '=', True), ('project_id', '=?', project_id)]")
    project_id = fields.Many2one(
        'project.project', 'Project', compute='_compute_project_id', store=True, readonly=False,
        domain=_domain_project_id)
    name = fields.Char('Comments', required=False, default=_default_name)

    # new fields
    display_name = fields.Char('Description', required=False, store=False, compute='_compute_display_name')
    rocker_type = fields.Selection([
        ('internal', 'Internal'),
        ('billable', 'Billable'),
        ('nonbillable', 'Non Billable')], 'Project Type', required=False, default='', store=False, related='project_id.rocker_type')
    task_search = fields.Many2one(
        'rocker.task', 'Project', store=True, readonly=False, required=False)
    rocker_search_type = fields.Selection([
        ('all', 'All'),
        ('mine', 'My Tasks'),
        ('billable', 'Billable'),
        ('nonbillable', 'Non Billable')], 'Search Type', store=False, required=False, default='all')
    #required fields
    # changed to non required, we handle this in views, (otherwise old timesheet app does not work)
    start = fields.Datetime(
        'Start', required=False, readonly=False, default=_default_start, store=True,
        help="Start datetime of a task")
    stop = fields.Datetime(
        'Stop', required=False, readonly=False, default=_default_stop, store=True,
        help="Stop datetime of a task")
    allday = fields.Boolean('All Day', default=False, required=False) # required in order calendar to work
    #
    daystocreateshow = fields.Integer('Generate', required=False, readonly=True, store=False,help="Create number of timeheet rows")
    duration = fields.Float('Duration', store=True, readonly=False, default=_default_duration, required=True, help="Work duration in hours")

    # existing fields
    date = fields.Date('Date', required=True, index=True, default=_default_date, store=True)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user, required=True)
    employee_id = fields.Many2one('hr.employee', "Employee",
        default=lambda self: self.env['hr.employee'].search([('user_id', '=', self.env.user.id), ('company_id','=',self.env.company.id)]).id, store=True)
    department_id = fields.Many2one('hr.department', "Department", compute='_compute_department_id', store=True, compute_sudo=True)
    unit_amount = fields.Float('Actual Work', default=_default_work, required=True, help="Work amount in hours")

    @api.depends('task_id', 'task_id.project_id')
    def _compute_project_id(self):
        _logger.debug('api depends task')
        if not self.task_id and self._get_search_id() > 0:
            _logger.debug('api depends...Task selected from searchpanel')
            search_task = self.env['project.task'].search([('id', '=', self._get_search_id())], limit=1)
            if not search_task.id:
                _logger.debug('Task not found from project.task...')
                # raise UserError(_('Project & Task not found'))   # this blocks original timesheet app row creation
                return False
            self.task_id = search_task.id
        for line in self.filtered(lambda line: not line.project_id):
            line.project_id = line.task_id.project_id

    @api.depends('project_id')
    def _compute_task_id(self):
        _logger.debug('api depends project')
        for line in self.filtered(lambda line: not line.project_id):
            line.task_id = False


    @api.depends('name','unit_amount')
    def _compute_display_name(self):
        _logger.debug('compute_display_name')
        for line in self:
            line.display_name = "%s %s %0.1f %s" % (line.name or '', ', ', line.unit_amount or 0, ' h')

    @api.depends('date')
    def _compute_date(self):
        _logger.debug('compute_date')
        self.ensure_one()
        self.date = self.start,date()

    @api.depends('user_id')
    def _compute_employee_id(self):
        _logger.debug('compute_employee_id')
        for line in self.filtered(lambda line: not line.employee_id):
            line.employee_id = line.user_id.employee_id

    @api.depends('employee_id')
    def _compute_department_id(self):
        _logger.debug('compute_department_id')
        for line in self:
            line.department_id = line.employee_id.department_id or line.user_id.employee_id.department_id  # single or multi company

    @api.depends('employee_id')
    def _compute_company_id(self):
        _logger.debug('compute_company_id')
        for line in self:
            line.company_id = line.employee_id.company_id


    #############################
    # read search create unlink
    #############################

    @api.model
    def create(self, vals):
        _logger.debug('Create...')

        # date exist on view
        if 'date' in vals and not vals.get('date'):
            vals['date'] = fields.Datetime.from_string(vals['start']).date()

        _selected_id = -1
        if vals.get('task_id') == False:
            _logger.debug('Task selected from searchpanel')
            _selected_id = _get_search_id()
            if _selected_id > 0:
                _logger.debug('Selected id set, search task...')
                search_task = self.env['project.task'].search([('id', '=', _selected_id)], limit=1)
                if not search_task.id:
                    _logger.debug('Task not found from project.task...')
                    return False
                _logger.debug('set vals task_id: ' + str(search_task.id))
                _logger.debug('set vals project_id: ' + str(search_task.project_id.id))
                vals['task_id'] = search_task.id
                vals['project_id'] = search_task.project_id.id
            else:
                raise UserError(_('Select Project & Task from drop-down fields'))
        if vals['name'] == False:
            if vals.get('task_id'):
                _name = self.env['project.task'].browse(vals['task_id']).name
            if _name:
                vals['name'] = _name
        _logger.debug('Calling super...')
        _logger.debug(vals)
        record = super(RockerTimesheet, self).create(vals)
        global daystocreate
        if daystocreate > 0:
            i = 0
            while i < daystocreate:
                _logger.debug('Create more ' + str(i) )
                vals['date'] = fields.Datetime.from_string(vals['date']) + timedelta(days=1)
                vals['start'] = fields.Datetime.from_string(vals['start']) + timedelta(days=1)
                vals['stop'] = fields.Datetime.from_string(vals['stop']) + timedelta(days=1)
                record = super(RockerTimesheet, self).create(vals)
                i += 1
        return record


    def read(self, values):
        _logger.debug('Read...')
        try:
            records = super(RockerTimesheet, self).read(values)
            return records
        except Exception as e:
            raise exceptions.ValidationError(str(e))
            return False

    def write(self, vals):
        _logger.debug('Write...')
        _logger.debug(vals)
        if vals.get('duration'):
            if vals['duration'] > 24:
                raise UserError(_('One timesheet row per day...duration can not exceed 24'))
        if vals.get('duration') and not vals.get('unit_amount') :
            vals['unit_amount'] = vals['duration']

        if not vals.get('date') and vals.get('start') : # case user has moved box in calendar view
            _logger.debug('date change')
            vals['date'] = fields.Datetime.from_string(vals['start']).date()

        result = super(RockerTimesheet, self).write(vals)
        return result


    # ----------------------------------------------------------
    # SearchPanel
    # ----------------------------------------------------------

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        args = args + self._domain_project_id_search()
        _logger.debug('Search...' + str(args))
        clause = []
        selected_id = 0
        i = 0
        for clause in args:
            if clause[0] == 'task_search':
                # selected_id = int(clause[2])
                if int(clause[2]) > 0: # id > 0 when task, project row has < 1
                    self._set_search_id( int(clause[2]) )
                clause[0] = 'task_search'
                clause[1] = '<>'
                clause[2] = ' '
                # del args[i] # don't know if there is & in front ??
            i += 1
        _logger.debug('Fixed search domain...' + str(args))
        _logger.debug('Selected id set: ' + str(self._get_search_id()))
        records = super(RockerTimesheet, self).search(args, limit=limit)
        return records

    @api.model
    def search_panel_select_range(self, field_name, **kwargs):
        _logger.debug('Search panel select range...')
        _logger.debug(kwargs.get('search_domain', []))
        global prev_company
        _logger.debug('env.company.id: ' +  str(self.env.company.id))
        _logger.debug('prev_company: ' +  str(prev_company))
        _logger.debug('new company: ' +  str(self.env.company.id) + ' prev company...' + str(prev_company))
        _company_changed = False
        if prev_company != self.env.company.id:
        # we need to refresh searchpanel,someone changed company :-)
            prev_company = self.env.company.id
            _logger.debug('company changed')
            _company_changed = True
            self._domain_set_search_filter('all')
        if field_name == 'task_search':
            if self._domain_get_search_filter() == "":
                self._domain_set_search_filter('all')
            _logger.debug('Setting new search values')
            search_domain = self._domain_get_search_domain(self._domain_get_search_filter())
            _logger.debug('New search domain:  ' + str(search_domain))
            # this works in Odoo 14
            return super(RockerTimesheet, self).search_panel_select_range(
                field_name, comodel_domain=search_domain, **kwargs
            )
            # odoo 13, does not work in odoo 14 (no hierarchy)
            # field = self._fields[field_name]
            # Comodel = self.env[field.comodel_name]
            # fields = ['display_name']
            # parent_name = Comodel._parent_name if Comodel._parent_name in Comodel._fields else False
            # if parent_name:
            #     fields.append(parent_name)
            # return {
            #     'parent_field': parent_name,
            #     'values': Comodel.with_context(hierarchical_naming=False).search_read(search_domain, fields),
            # }

        return super(RockerTimesheet, self).search_panel_select_range(field_name, **kwargs)

    def searchpanel_all(self, filt):
        _logger.debug('Searchpanel_all...')
        if filt == 'all':
            self._domain_set_search_filter('all')
        elif filt == 'member':
            self._domain_set_search_filter('member')
        elif filt == 'billable':
            self._domain_set_search_filter('billable')
        elif filt == 'nonbillable':
            self._domain_set_search_filter('nonbillable')
        elif filt == 'internal':
            self._domain_set_search_filter('internal')
        elif filt == 'mine':
            self._domain_set_search_filter('mine')
        else:
            self._domain_set_search_filter('all')
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }


    @api.model
    def get_unusual_days(self, date_from, date_to=None):
        # Checking the calendar directly allows to not grey out the leaves taken
        # by the employee
        calendar = self.env.user.employee_id.resource_calendar_id
        if not calendar:
            return {}
        tz = pytz.timezone('UTC')
        usertime = pytz.utc.localize(datetime.now()).astimezone(tz)
        dfrom = pytz.utc.localize(datetime.combine(fields.Date.from_string(date_from), time.min)).astimezone(tz)
        dto = pytz.utc.localize(datetime.combine(fields.Date.from_string(date_to), time.max)).astimezone(tz)

        works = {d[0].date() for d in calendar._work_intervals_batch(dfrom, dto)[False]}
        return {fields.Date.to_string(day.date()): (day.date() not in works) for day in rrule(DAILY, dfrom, until=dto)}

    @api.onchange('start')
    def _onchange_start(self):
        _logger.debug('_onchange_start')
        if not self.start:
            return False
        global daystocreate
        daystocreate = 0
        _delta = 0
        if self.stop and self.start:
            _delta = self.stop.date() - self.start.date()
            daystocreate = _delta.days
        _logger.debug('Needs to create ' + str(daystocreate) + ' extra timesheet rows')

        self.date = self.start.date()

        fmt = "%Y-%m-%d %H:%M"
        _dt = fields.Datetime.from_string(self.start).time()
        if  (_dt.hour == 0 and _dt.minute == 0 and _dt.second == 0) or self.stop.date() > self.start.date():
            _logger.debug('times are zero')
            self.daystocreateshow = daystocreate + 1
            self.start = (fields.Datetime.from_string(self.start.date()) + timedelta(hours=self._default_start_time())).strftime(fmt)
            # change to create only one day, create() then generates more days
            self.stop = (fields.Datetime.from_string(self.start.date()) + timedelta(hours=self._default_end_time())).strftime(fmt)
            self.duration = self._get_duration(self.start,self.stop)
            self.unit_amount = self._default_work()
            _logger.debug('UNIT_AMOUNT: ' + str(self.unit_amount))
            self.allday = False
        else:
            _logger.debug('on change start else...')
            self.stop = fields.Datetime.from_string(self.start) + timedelta(hours=self.duration)
            self.date = fields.Datetime.from_string(self.start).date()
            self.duration = self._get_duration(self.start, self.stop)
            self.unit_amount = self.duration
            _logger.debug('UNIT_AMOUNT: ' + str(self.unit_amount))
            self.daystocreateshow = 0

    @api.onchange('duration')
    def _onchange_duration(self):
        _logger.debug('onchange_duration')
        self.stop = fields.Datetime.from_string(self.start) + timedelta(hours=self.duration)

    @api.onchange('stop')
    def _onchange_stop(self):
        _logger.debug('onchange_stop')
        if fields.Datetime.from_string(self.stop) < fields.Datetime.from_string(self.start):
            raise UserError(_('Stop before start!'))
        self.duration = self._get_duration(self.start,self.stop)
