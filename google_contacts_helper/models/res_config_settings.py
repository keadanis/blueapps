from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # to be used in the general settings page
    module_google_contacts = fields.Boolean(string='Synchronize Google contacts')
