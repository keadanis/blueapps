# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"
    _description = "Warehouse"


    @api.onchange('name')
    def _name_maj_warehouse(self):
        self.name = self.name.title() if self.name else False
         
    @api.onchange('code')
    def _code_maj_warehouse(self):
        self.code = self.code.title() if self.code else False