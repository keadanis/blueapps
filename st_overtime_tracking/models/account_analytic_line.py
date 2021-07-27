# encoding: utf-8

from odoo import api, models


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'
    
    @api.model
    def create(self,vals_list):
        lines = super().create(vals_list)
        projects = lines.mapped('project_id')
        dates = lines.mapped('date')
        self._recompute_tracks(projects,dates)
        return lines
    
    def write(self,vals):
        recompute = False
        if any(True for tmp_key in ['unit_amount','project_id','date'] if tmp_key in vals):
            recompute = True
            projects = self.mapped('project_id')
            dates = self.mapped('date')
        result = super().write(vals)
        if recompute:
            projects |= self.mapped('project_id')
            dates.extend(self.mapped('date'))
            self._recompute_tracks(projects,dates)
        return result
    
    def unlink(self):
        projects = self.mapped('project_id')
        dates = self.mapped('date')
        result = super().unlink()
        self._recompute_tracks(projects,dates)
        return result
    
    def _recompute_tracks(self,projects,dates):
        to_recompute_tracks = self.env['hr.track'].search([
            ('project_ids','in',projects.ids),
            ('start_date','<=',min(dates)),
            ('end_date','>=',max(dates)),
            ])
        to_recompute_tracks._compute_current_hours()
    
    
    