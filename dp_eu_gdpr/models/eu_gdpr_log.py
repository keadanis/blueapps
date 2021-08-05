# Copyright 2018-Today datenpol gmbh (<https://www.datenpol.at/>)
# License OPL-1 or later (https://www.odoo.com/documentation/user/13.0/legal/licenses/licenses.html#licenses).

from odoo import fields, models, _


class GDPRLog(models.Model):
    _name = 'eu.gdpr_log'
    _description = 'GDPR Log'
    _order = 'create_date DESC'

    name = fields.Char('Name', compute='_compute_name')
    date = fields.Datetime('Creation date', required=True, default=fields.Datetime.now())
    user_id = fields.Many2one('res.users', 'User', required=True, default=lambda self: self._uid)
    operation = fields.Char('Operation')
    object = fields.Char('Object')
    dataset = fields.Char('Data Set')
    partner = fields.Char('Partner', help='Person who executed the operation (e. g. Customer)')
    note = fields.Char('Notes')

    def _compute_name(self):
        for record in self:
            record.name = _('EU-GDPR Log Entry #%s') % record.id
