from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    partner_tags = fields.Many2many(
        related="partner_id.category_id",
        string="Partner Tags"
    )
