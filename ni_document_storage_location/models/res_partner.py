from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    document_storage_ids = fields.One2many('document.storage','partner_id',string='Document')
    document_storage_count = fields.Integer('Document Count', compute="_compute_document_storage_count")

    def _compute_document_storage_count(self):
        for record in self:
            record.document_storage_count = len(record.document_storage_ids)
            