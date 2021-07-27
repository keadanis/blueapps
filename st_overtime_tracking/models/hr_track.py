# encoding: utf-8

from odoo import api, fields, models


class HrTrack(models.Model):
    _name = 'hr.track'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'Overtime Tracking'
    
    
    name = fields.Char('Name')
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    target_hours= fields.Float('Target Hours')
    current_hours = fields.Float('Current Hours', compute='_compute_current_hours', store=True)
    project_ids = fields.Many2many('project.project',string='Projects')
    difference = fields.Float('Difference', compute='_compute_difference', store=True)
    
    @api.depends('start_date','end_date','project_ids')
    def _compute_current_hours(self):
        line_obj = self.env['account.analytic.line']
        for track in self:
            lines = line_obj.search([
                ('project_id','in',track.project_ids.ids),
                ('date','>=',track.start_date),
                ('date','<=',track.end_date)
                ])
            track.current_hours = lines and sum(lines.mapped('unit_amount')) or 0
            
    @api.depends('target_hours','current_hours')
    def _compute_difference(self):
        for track in self:
            track.difference = track.current_hours - track.target_hours
        
    
    
    