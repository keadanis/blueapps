# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions


class ProductTemplate(models.Model):
    _inherit = 'product.template'
     
    _sql_constraints = [('product_template_name_uniqu', 'unique(name)', 'Product already exist!')]
     
    @api.onchange('name')
    def _compute_maj_temp(self):
        self.name = self.name.title() if self.name else False
        
class ProductProduct(models.Model):
    _inherit = 'product.product'
     
    _sql_constraints = [('product_product_name_uniqu', 'unique(name)', 'Product already exist!')]

    @api.onchange('name')
    def _compute_maj_pro(self):
        self.name = self.name.title() if self.name else False
