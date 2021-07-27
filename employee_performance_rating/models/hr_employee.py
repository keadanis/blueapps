from odoo import fields, models, api


class Employee(models.Model):
    _inherit = 'hr.employee'

    performance_rating = fields.Selection([
        ('outstanding', 'Outstanding'),
        ('verysatisfactory', 'Very Satisfactory'),
        ('satisfactory', 'Satisfactory'),
        ('unsatisfactory', 'Unsatisfactory'),
        ('poor', 'Poor')], string='Performance Rating')