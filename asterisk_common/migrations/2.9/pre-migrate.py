# ©️ OdooPBX by Odooist, Odoo Proprietary License v1.0, 2020
import logging
from odoo import api, SUPERUSER_ID

logger = logging.getLogger(__name__)


def migrate(cr, version):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        res = env['ir.model.data'].search([('name', '=', 'fully_booted'),
                                          ('module', '=', 'asterisk_common')])
        if res:
            # Rename fully_booted to originate_response as in new data file.
            res.name = 'originate_response'
