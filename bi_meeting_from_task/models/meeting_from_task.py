# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import datetime, timedelta

class ProjectTask(models.Model):
    _inherit = 'project.task'

    meeting_id = fields.Many2one('calendar.event', string="Meeting", readonly=True)
    meeting_count = fields.Integer('Meeting',compute='_compute_meeting')

    # count meeting
    @api.depends('meeting_id')
    def _compute_meeting(self):
        self.meeting_count = self.env['calendar.event'].search_count([('task_id','=',self.id)])

class CalenderEvent(models.Model):
    _inherit = 'calendar.event'

    task_id = fields.Many2one('project.task', string="Task", readonly=True)
    project_id = fields.Many2one('project.project',string="Project")
    task_count = fields.Integer('Tasks', compute='_compute_task',)

    # count task 
    @api.depends('task_id')
    def _compute_task(self):
        self.task_count = self.env['project.task'].search_count([('meeting_id','=',self.id)])

class MeetingDate(models.TransientModel):
    _name = 'meeting.date'
    _description = "Create Meeting from Task"

    start_date = fields.Datetime('Meeting Date', required=True)
    
    def get_data(self):
        task_obj= self.env['project.task'].browse(self._context.get('active_ids'))
        calendar_obj = self.env['calendar.event'].create({'name':"Meeting from : "+task_obj.name , 'start':str(self.start_date),'duration':1, 'stop':self.start_date + timedelta(hours=1),'task_id':task_obj.id, 'project_id':task_obj.project_id.id})
        task_obj.write({'meeting_id':calendar_obj.id})