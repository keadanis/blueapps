# ©️ OdooPBX by Odooist, Odoo Proprietary License v1.0, 2020
import logging
from odoo import api, SUPERUSER_ID

logger = logging.getLogger(__name__)


def migrate(cr, version):
    try:
        with api.Environment.manage():
            env = api.Environment(cr, SUPERUSER_ID, {})
            for user in env['asterisk_common.user'].search([]):
                current_vars = user.originate_vars
                if current_vars:
                    current_vars = current_vars.split('\n')
                    for var in current_vars:
                        if 'HEADER' in var and 'SIP' in var and '=' in var:
                            current_vars.remove(var)
                    user.originate_vars = '\n'.join(current_vars)
    except Exception as e:
        logger.warning(
            'Asterisk Common user channel migration non-critical error: %s', e)
