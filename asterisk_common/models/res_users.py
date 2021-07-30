# ©️ OdooPBX by Odooist, Odoo Proprietary License v1.0, 2020
import logging
from odoo import models, fields, api, tools, release, _
from odoo.exceptions import ValidationError, UserError

logger = logging.getLogger(__name__)


class ResUser(models.Model):
    _inherit = 'res.users'

    remote_agent = fields.One2many('remote_agent.agent', inverse_name='user')
    asterisk_users = fields.One2many(
        'asterisk_common.user', inverse_name='user', readonly=True)
    # Primary user & system used to originate clic2dial calls.
    asterisk_user = fields.Many2one('asterisk_common.user', store=True,
                                    compute='_get_asterisk_user')
    asterisk_agent = fields.Many2one('remote_agent.agent',
                                     compute='_get_asterisk_agent')

    @api.model
    def asterisk_notify(self, message, title='PBX', uid=None,
                        sticky=False, warning=False):
        if self.env.context.get('disable_notify'):
            return True
        if not uid:
            uid = self.env.uid
        self.env['bus.bus'].sendone(
            'remote_agent_notification_{}'.format(uid),
            {'message': message, 'title': title,
             'sticky': sticky, 'warning': warning})
        return True

    @api.depends('asterisk_users')
    def _get_asterisk_user(self):
        for rec in self:
            found = False
            for asterisk_user in rec.asterisk_users:
                if asterisk_user.is_primary_system:
                    rec.asterisk_user = asterisk_user.id
                    found = True
                    continue
            if not found:
                rec.asterisk_user = False

    def _get_asterisk_agent(self):
        self.ensure_one()
        for rec in self:
            if rec.remote_agent:
                # Agent account
                rec.asterisk_agent = rec.remote_agent
            elif rec.asterisk_user.agent:
                # User account
                rec.asterisk_agent = rec.asterisk_user.agent

