# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
     

class UniquePartner(models.Model):
    _inherit = 'res.partner'

    _sql_constraints = [('res_partner_name_uniqu', 'unique(name)', 'Name of partner already exist !')]
     
    @api.onchange('name')
    def _compute_maj_par(self):
        self.name = self.name.title() if self.name else False
