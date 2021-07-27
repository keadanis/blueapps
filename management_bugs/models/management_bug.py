# -*- coding: utf-8 -*-
import glob
import os
import shutil

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError, ValidationError


class ManagementBug(models.Model):
    _name = 'management.bug'
    _description = 'Management bug'
    _order = 'id'

    name = fields.Char(string='Name', required=True, translate=True)
    code = fields.Char('Code')
    date_error = fields.Date('Date error')
    hour_error = fields.Char('Hours')
    description = fields.Text('Description')
    type_bug = fields.Selection([
        ('error', 'Error'),
        ('warning', 'Warning')], 'Type Bug', track_visibility='always', default=lambda self: self._context.get('type', 'warning'))
    line = fields.Char('Line')
    project_id = fields.Many2one('project.project', 'Projects', track_visibility='onchange')
    active = fields.Boolean('Active', default=True)
    state = fields.Selection([
        ('unresolved', 'Unresolved'),
        ('resolved', 'Resolved')], 'Status', track_visibility='onchage', default='unresolved')
    note = fields.Text('Notes')

    def read_route_file(self, route):
        name_route = ''
        if glob.glob(route + '/*'):
            list_path = glob.glob(route + '/*.log')
            for name in list_path:
                separate_name = name.split('/')[-1:]
                if separate_name[0] == 'odoo.log':
                    name_route = name
        return name_route

    def action_check_all_bugs(self):
        dict_error = {
            'name': '',
            'code': '',
            'date_error': False,
            'hour_error': False,
            'description': '',
            'type_bug': False,
            'line': ''
        }
        dict_init = {
            'name': '',
            'code': '',
            'date_error': False,
            'hour_error': False,
            'description': '',
            'type_bug': False,
            'line': ''
        }
        details_line = 0
        name_error = 'ERROR-'
        name_warn = 'WARNING-'
        list_display = []
        # data configuration
        obj_setting_id = self.env['configuration.bug'].search([('active', '=', True)])
        if obj_setting_id:
            for obj_setting in obj_setting_id:
                route = obj_setting.route
        file_touch = self.read_route_file(route)
        if file_touch:
            # copy log
            destination_route = '/tmp/' + 'new_log.log'
            if os.path.exists(file_touch):
                with open(file_touch, 'rb') as forigen:
                    with open(destination_route, 'wb') as fdestino:
                        shutil.copyfileobj(forigen, fdestino)
            # read log new
            if os.path.exists(destination_route):
                file_lines = open(destination_route, 'r')
                for line in file_lines:
                    details_line += 1
                    count_character = 0
                    line = line.split(' ')
                    if 'ERROR' in line or 'WARNING' in line:
                        dict_error['date_error'] = line[0]
                        dict_error['hour_error'] = line[1]
                        dict_error['code'] = line[2]
                        dict_error['description'] = line[-1]
                        dict_error['line'] = details_line
                        if 'ERROR' in line:
                            dict_error['name'] = name_error + line[2]
                            dict_error['type_bug'] = 'error'
                            for i in line:
                                list_display = line
                                if i != 'ERROR':
                                    count_character += 1
                                    if count_character <= 4:
                                        list_display.pop(0)
                            dict_error['description'] = " ".join(list_display)
                        else:
                            dict_error['name'] = name_warn + line[2]
                            dict_error['type_bug'] = 'warning'
                            for i in line:
                                list_display = line
                                if i != 'WARNING':
                                    count_character += 1
                                    if count_character <= 4:
                                        list_display.pop(0)
                            dict_error['description'] = " ".join(list_display)
                        create_bug = self.env['management.bug']
                        # create model (data)
                        if len(dict_error) > 0:
                            # eliminar los que tengan valor False
                            dict_error = dict(filter(lambda x: x[1] != False, dict_error.items()))
                            # crear bug
                            create_bug.create(dict_error)
                            dict_error.update(dict_init)
        # delete new log
        file_lines.close()
        os.remove(destination_route)

    def action_claim_bug(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            compose_form_id = ir_model_data.get_object_reference('management_bugs', 'management_bug_assign_form_me')[1]
        except ValueError:
            compose_form_id = False
        return {
            "name": "Claim a Bugs",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "management.bug.assign",
            "type": "ir.actions.act_window",
            'view_id': compose_form_id,
            'target': 'new',
        }

    def action_to_assign_bug(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            compose_form_id = ir_model_data.get_object_reference('management_bugs', 'management_bug_assign_form')[1]
        except ValueError:
            compose_form_id = False
        return {
            "name": "Transfer or Assign",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "management.bug.assign",
            "type": "ir.actions.act_window",
            'view_id': compose_form_id,
            'target': 'new',
        }


class ConfigurationBug(models.Model):
    _name = "configuration.bug"
    _description = "Configuration Bug"

    name = fields.Char(string='Name', required=True, translate=True)
    active = fields.Boolean('Active')
    route = fields.Char('Route', required=True, help='The path to the file should contain the container folders, Ex: /var/log/..')

    @api.constrains('route')
    def _add_constrains_fields(self):
        if self.route:
            if not self.route == '/var/log/odoo':
                raise ValidationError("The route of the file should are '/var/log/odoo' .")


class ManagementBugAssign(models.TransientModel):
    _name = "management.bug.assign"
    _description = "Management bug assign"
    _rec_name = 'type_assign'

    type_assign = fields.Selection([
        ('agent', 'Agent'),
        ('team', 'Team Support')], 'Assign', track_visibility='onchage', default='agent', required=True, index=True)
    user_id = fields.Many2one('res.users', 'User')
    support_id = fields.Many2one('team.support', 'Team Support')
    project_id = fields.Many2one('project.project', 'Projects', track_visibility='onchange')
    note = fields.Text('Note')

    def action_do_transfer(self):
        self.ensure_one()
        dict_task = {
            'name': '',
            'project_id': '',
            'user_id': '',
            'support_id': '',
            'description': ''
        }
        name_task = ''
        active_bug_ids = self.env.context.get('active_ids', [])
        for bug in self.env['management.bug'].sudo().browse(active_bug_ids):
            # make sure that each bug appears at most once in the list
            if self.note:
                if not bug.note:
                    bug.note = ''
                bug.note += str(self.env.user.name) + ': ' + self.note + ' \n' + ' \n'
            create_task = self.env['project.task']
            if bug.type_bug:
                if bug.type_bug == 'error':
                    name_task = '[Develop] ' + bug.name
                if bug.type_bug == 'warning':
                    name_task = '[Support] ' + bug.name
            dict_task['name'] = name_task
            if self.project_id:
                for project in self.env['project.project'].sudo().browse(self.project_id):
                    dict_task['project_id'] = project.id['id']
                    if self.project_id.user_id:
                        obj_support_id = self.env['team.support'].search([('leader_id', '=', self.project_id.user_id.id)])
                        if obj_support_id:
                            for support in obj_support_id:
                                list_members = support.member_ids
                                if list_members:
                                    if self.user_id in list_members:
                                        if self.type_assign == 'agent':
                                            dict_task['user_id'] = self.user_id.id
                                            dict_task['support_id'] = support.id
                        #         else:
                        #             raise UserError(_('The support team does not has a team leader'))
                        # else:
                        #     raise UserError(_('The support team does not has a members'))

            if self.support_id:
                obj_support_id = self.env['team.support'].search([('id', '=', self.support_id.id)])
                if obj_support_id:
                    for obj_support in obj_support_id:
                        dict_task['support_id'] = obj_support.id
                        dict_task['user_id'] = self.project_id.user_id.id
            dict_task['description'] = bug.description
            create_task.create(dict_task)
            bug.state = 'resolved'

    def action_do_claim(self):
        self.ensure_one()
        dict_task = {
            'name': '',
            'project_id': '',
            'user_id': '',
            'description': ''
        }
        name_task = ''
        active_bug_ids = self.env.context.get('active_ids', [])
        for bug in self.env['management.bug'].sudo().browse(active_bug_ids):
            # make sure that each bug appears at most once in the list
            if self.note:
                if not bug.note:
                    bug.note = ''
                bug.note += str(self.env.user.name) + ': ' + self.note + ' \n' + ' \n'
            create_task = self.env['project.task']
            if bug.type_bug:
                if bug.type_bug == 'error':
                    name_task = '[Develop] ' + bug.name
                if bug.type_bug == 'warning':
                    name_task = '[Support] ' + bug.name
            dict_task['name'] = name_task
            if self.project_id:
                for project in self.env['project.project'].sudo().browse(self.project_id):
                    dict_task['project_id'] = project.id['id']
                    dict_task['user_id'] = self.env.user.id
            dict_task['description'] = bug.description
            create_task.create(dict_task)
            bug.state = 'resolved'


class TeamSupport(models.Model):
    _name = 'team.support'
    _description = 'Team support'

    name = fields.Char('Name', index=True, required=True)
    leader_id = fields.Many2one('res.users', 'Leader')
    member_ids = fields.Many2many('res.users', 'team_user_support_rel', 'support_id', 'user_id', 'Members')


class Task(models.Model):
    _inherit = "project.task"

    support_id = fields.Many2one('team.support', 'Team Support')
