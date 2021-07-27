# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions


class maj_uniq_employee(models.Model):
    _inherit = 'hr.employee'

    _sql_constraints = [('hr_employee_name_uniqu', 'unique(name)', 'Employee already exist !')]
     
    @api.onchange('name')
    def _compute_maj_employee(self):
        self.name = self.name.title() if self.name else False
        
class maj_uniq_department(models.Model):
    _inherit = 'hr.department'

    _sql_constraints = [('hr_department_name_uniqu', 'unique(name)', 'Department already exist !')]
     
    @api.onchange('name')
    def _compute_maj_depart(self):
        self.name = self.name.title() if self.name else False
        