# Copyright 2018-Today datenpol gmbh (<https://www.datenpol.at/>)
# License OPL-1 or later (https://www.odoo.com/documentation/user/13.0/legal/licenses/licenses.html#licenses).

import base64
from io import BytesIO
import zipfile

from odoo.tests.common import TransactionCase


class TestDpEuGdpr(TransactionCase):
    """
    General Data Protection Regulation (GDPR) Tests

    We only test res.partner and res.users. This works because they are part
    of the base module. It's not possible to test the other supported objects
    when running within the Odoo test framework since that would require to
    add their modules to our dependencies. But we can't do that to keep them
    optional. It should be possible to test the other objects when running the
    tests with pytest. However these would have to be separate then so that
    Odoo's test runner doesn't see them.
    """

    def setUp(self):
        super().setUp()

        self.wizard = self.env['eu.gdpr'].create({})
        self.demo_customer = self.env.ref('base.res_partner_12')
        self.demo_user = self.env.ref('base.user_demo')


    def test_operation_access(self):
        """
        Call the export function and check if name is returned correctly
        """

        # res.partner
        self.wizard.object = "%s,%s" % (self.demo_customer._name, str(self.demo_customer.id))
        _, line = self.wizard._prepare_export_data()
        assert line[0] == self.demo_customer.name

        # res.users
        self.wizard.object = "%s,%s" % (self.demo_user._name, str(self.demo_user.id))
        _, line = self.wizard._prepare_export_data()
        assert line[0] == self.demo_user.name


    def test_operation_access_returns_zip(self):
        """
        Run wizard and export customer data, check if a zip file is created
        """

        self.wizard.object = "%s,%s" % (self.demo_customer._name, str(self.demo_customer.id))
        log = self.env['eu.gdpr_log'].create({})
        attachment_id = self.wizard._export_csv(log)
        attachment = self.env['ir.attachment'].browse(attachment_id)
        zipdata = BytesIO(base64.b64decode(attachment.datas))
        assert zipfile.is_zipfile(zipdata)


    def test_operation_erasure_unlink(self):
        """
        Objects must be unlinked during erasure where possible.

        In this case we create new objects so they aren't referenced anywhere
        else and unlinking is possible.

        dp-Österreich 732: EU-DSGVO
        """

        self.wizard.operation = 'erasure'

        # res.partner
        ResPartner = self.env['res.partner']

        vals = {
            'name': 'Herbert Hrabal',
        }
        partner = ResPartner.create(vals)

        self.wizard.object = "%s,%s" % (partner._name, str(partner.id))
        self.wizard.process()

        domain = [
            ('name', '=', 'Herbert Hrabal'),
        ]
        assert ResPartner.search_count(domain) == 0

        # res.users
        ResUsers = self.env['res.users']

        vals = {
            'name': 'Dorothea Tiefenthal',
            'login': 'doro@example.com',
        }
        user = self.env['res.users'].create(vals)
        partner_id = user.partner_id.id

        self.wizard.object = "%s,%s" % (user._name, str(user.id))
        self.wizard.process()

        domain = [
            ('name', '=', 'Dorothea Tiefenthal'),
        ]
        assert ResUsers.search_count(domain) == 0

        assert not ResPartner.browse(partner_id).exists()


    def test_operation_restriction(self):
        """
        Objects must become inactive during restriction.

        dp-Österreich 732: EU-DSGVO
        """

        self.wizard.operation = 'restrict'

        # res.partner
        assert self.demo_customer.active

        self.wizard.object = "%s,%s" % (self.demo_customer._name, str(self.demo_customer.id))
        self.wizard.process()

        assert not self.demo_customer.active

        # res.users
        assert self.demo_user.active

        self.wizard.object = "%s,%s" % (self.demo_user._name, str(self.demo_user.id))
        self.wizard.process()

        assert not self.demo_user.active
        assert not self.demo_user.partner_id.active
