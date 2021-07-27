from odoo import api, fields, models, _


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    document_storage_ids=fields.One2many('document.storage','employee_id',string='Document')
    document_storage_count = fields.Integer('Document Count', compute="_compute_document_storage_count")

    def _compute_document_storage_count(self):
        for record in self:
            record.document_storage_count = len(record.document_storage_ids)
