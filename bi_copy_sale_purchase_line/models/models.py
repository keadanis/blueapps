# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class TraineeManagement(models.Model):
    _name = 'trainee.management'
    _description = 'Trainee Management'

    name = fields.Char(string='Name')
    boolean_field = fields.Boolean(
        string='Boolean Field')
    char_field = fields.Char(
        string='Char Field',
    )
    float_field = fields.Float(
        string='Float Field',
    )
    integer_field = fields.Integer(
        string='Integer Field',
    )
    binary_field = fields.Binary(
        string='Binary Field',
        attachment=True,
    )
    html_field = fields.Html(
        string='HTML Field',
    )
    select_field = fields.Selection([
        ('male','Male'),
        ('female','Female'),
        ('other', 'Other')],default="male") 
    image_field = fields.Binary(string="Logo")

    datetime_field = fields.Datetime(
        string='Datetime Field',
    )

    date_field = fields.Date(
        string='Field Label'
    )

    text_field = fields.Text(
        string='Text Field',
    )


class SaleOrder(models.Model):
    _inherit = 'sale.order.line'

    def copy_sale_order_line(self):
        self.copy(default={'order_id': self.order_id.id})


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def copy_purchase_order_line(self):
        self.copy(default={'order_id': self.order_id.id})

