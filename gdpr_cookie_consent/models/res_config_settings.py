# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    privado_script_code_snippet = fields.Text(
        string='Privado Code Snippet',
        help='Code Snippet you can get it from https://privado.ai/')

    @api.model
    def set_values(self):
        self.env['ir.config_parameter'].sudo().set_param('gdpr_cookie_consent.privado_script_code_snippet',
                                                         self.privado_script_code_snippet)
        super(ResConfigSettings, self).set_values()

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res['privado_script_code_snippet'] = self.env['ir.config_parameter'].sudo().get_param(
            'gdpr_cookie_consent.privado_script_code_snippet', default='')
        return res
