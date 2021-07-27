# Copyright 2020 Manish Kumar Bohra <manishbohra1994@gmail.com> or <manishkumarbohra@outlook.com>
# License LGPL-3 - See http://www.gnu.org/licenses/Lgpl-3.0.html

from odoo import api, fields, models


class CRMReload(models.Model):
    _inherit = 'crm.lead'

    def crm_reload(self):
        """this method used to reload the sales order without reload webpage."""
        return {
            'type': 'ir.actions.client',
            'tag': 'trigger_reload'
        }
