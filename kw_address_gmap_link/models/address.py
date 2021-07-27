import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)


class AddressMixin(models.AbstractModel):
    _name = 'kw.address.gmap.link.mixin'
    _description = 'Address gmap link mixin'
    _inherit = 'kw.address.mixin'

    address_url = fields.Char(
        compute='_compute_address_url', )

    def _compute_address_url(self):
        for obj in self:
            a = [obj._get_country_name(), obj._get_state_name(), obj.city,
                 obj.street, ]
            obj.address_url = 'https://www.google.com/maps/search/{}' \
                              ''.format(', '.join([x for x in a if x]))


class Address(models.Model):
    _name = 'kw.address'
    _inherit = ['kw.address.gmap.link.mixin', 'kw.address', ]
