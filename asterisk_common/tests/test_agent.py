# ©️ OdooPBX by Odooist, Odoo Proprietary License v1.0, 2020
import logging
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from unittest.mock import patch, call
from ..models.res_users import ResUser
from ..models.agent import Agent

logger = logging.getLogger(__name__)


class TestAgent(TransactionCase):
    def setUp(self, *args, **kwargs):
        super(TestAgent, self).setUp(*args, **kwargs)
        self.agent = self.env.ref('asterisk_common.remote_agent')

    def test_db_name(self):
        self.assertEqual(self.env.cr.dbname, self.agent.current_db)
