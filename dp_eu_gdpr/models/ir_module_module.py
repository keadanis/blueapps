# -*- coding: utf-8 -*-
# Copyright 2018-Today datenpol gmbh (<http://www.datenpol.at>)
# License OPL-1 or later (https://www.odoo.com/documentation/user/12.0/legal/licenses/licenses.html#licenses).

from odoo import api, fields, models, _


class IrModuleModule(models.Model):
    _inherit = 'ir.module.module'

    def _button_immediate_function(self, function):
        res = super(IrModuleModule, self)._button_immediate_function(function)
        eu_gdpr = self.with_context(lang=self.env.user.lang).env['ir.model'].search([('model', '=', 'eu.gdpr')])
        if eu_gdpr and set(self.mapped('name')).intersection({'crm', 'base', 'hr', 'hr_recruitment'}):
            module = self.env['ir.module.module'].search([('name', '=', 'dp_eu_gdpr'), ('state', '=', 'installed')])
            module.button_upgrade()
        return res
