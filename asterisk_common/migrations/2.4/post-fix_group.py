# ©️ OdooPBX by Odooist, Odoo Proprietary License v1.0, 2020
import logging
from odoo import api, SUPERUSER_ID

logger = logging.getLogger(__name__)


def migrate(cr, version):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        if env.ref('base.user_admin') in env.ref(
                'asterisk_common.group_asterisk_user').users:
            # Unset user group for admin
            env.ref('asterisk_common.group_asterisk_user').users = [(3,
                                        env.ref('base.user_admin').id, 0)]
