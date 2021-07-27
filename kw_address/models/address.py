import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)

ADDRESS_FIELDS = ('street', 'street2', 'zip', 'city', 'state_id', 'country_id')


class AddressType(models.Model):
    _name = 'kw.address.type'
    _description = 'Address type'

    name = fields.Char()

    active = fields.Boolean(
        default=True, )


class AddressMixin(models.AbstractModel):
    _name = 'kw.address.mixin'
    _description = 'Address mixin'

    street = fields.Char()

    street2 = fields.Char()

    zip = fields.Char(
        change_default=True, )
    city = fields.Char()

    state_id = fields.Many2one(
        comodel_name='res.country.state', ondelete='restrict',
        domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one(
        comodel_name='res.country', ondelete='restrict')
    latitude = fields.Float(
        digits=(16, 5))
    longitude = fields.Float(
        digits=(16, 5))

    @api.model
    def _formatting_address_fields(self):
        return list(ADDRESS_FIELDS)

    def _get_country_name(self):
        self.ensure_one()
        return self.country_id.name or ''

    def _get_state_name(self):
        self.ensure_one()
        return self.state_id.name or ''

    @api.model
    def _get_default_address_format(self):
        return '%(street)s\n%(street2)s\n%(city)s %(state_code)s ' \
               '%(zip)s\n%(country_name)s'

    @api.model
    def _get_address_format(self):
        self.ensure_one()
        return self.country_id.address_format or \
            self._get_default_address_format()

    def _display_address(self):
        self.ensure_one()
        args = {
            'state_code': self.state_id.code or '',
            'state_name': self.state_id.name or '',
            'country_code': self.country_id.code or '',
            'country_name': self._get_country_name(), }
        for field in self._formatting_address_fields():
            args[field] = getattr(self, field) or ''
        return '%(street)s\n%(street2)s\n%(city)s %(state_code)s ' \
               '%(zip)s\n%(country_name)s' % args
        # return self._get_address_format() % args


class Address(models.Model):
    _name = 'kw.address'
    _description = 'Address'
    _inherit = 'kw.address.mixin'

    name = fields.Char(
        compute='_compute_name', store=True, )
    active = fields.Boolean(
        default=True, )
    type_id = fields.Many2one(
        comodel_name='kw.address.type', ondelete='restrict', )

    @api.depends('street', 'street2', 'zip', 'city', 'state_id', 'country_id')
    def _compute_name(self):
        for obj in self:
            obj.name = obj._display_address()
