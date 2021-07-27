# -*- coding: utf-8 -*-
# Copyright 2018, 2020 Heliconia Solutions Pvt Ltd (https://heliconia.io)

from odoo import models, fields, api, SUPERUSER_ID, _
from odoo.exceptions import AccessDenied, AccessError, UserError, ValidationError
from odoo.http import request
from odoo import http
import odoo
import logging

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

    @classmethod
    def _login(cls, db, login, password):
        if not password:
            return False
        user_id = False
        try:
            with cls.pool.cursor() as cr:
                self = api.Environment(cr, SUPERUSER_ID, {})[cls._name]
                # env = {'interactive': False}'   # added because need parameter
                user = self.search([('login', '=', login)])
                if user:
                    user_id = user.id
                    if type(request.params).__name__ == 'OrderedDict':
                        user.with_user(user_id)._check_credentials(password, {'interactive': False})
                        # user.with_user(user_id)._check_credentials(password)
                        user.with_user(user_id)._update_last_login()
                    else:
                        user.with_user(user_id)._update_last_login()

        except AccessDenied:
            user_id = False

        status = "successful" if user_id else "failed"
        ip = request.httprequest.environ['REMOTE_ADDR'] if request else 'n/a'
        _logger.info("Login %s for db:%s login:%s from %s", status, db, login, ip)

        return user_id

    @classmethod
    def authenticate(cls, db, login, password, user_agent_env):

        uid = cls._login(db, login, password)
        if uid == SUPERUSER_ID:
            if user_agent_env and user_agent_env.get('base_location'):
                try:
                    with cls.pool.cursor() as cr:
                        base = user_agent_env['base_location']
                        ICP = api.Environment(cr, uid, {})['ir.config_parameter']
                        if not ICP.get_param('web.base.url.freeze'):
                            ICP.set_param('web.base.url', base)
                except Exception:
                    _logger.exception("Failed to update web.base.url configuration parameter")
        return uid

    @api.model
    def check_for_user_simulation(self, user_id):
        # got the call here : we will check here the group and if it is simulated or not
        if request.session.get("is_simulated"):
            return True
        if user_id in [user.id for user in self.env.ref('hspl_user_simulation.group_user_simulation').users]:
            return True
        return False

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        if self.env.context.get('user_simulation_context'):
            user_ids = [user.id for user in self.env.ref('base.group_user').users]
            args = args or []
            args += [('id', 'in', user_ids)]
        return super(ResUsers, self).name_search(name=name, args=args, operator=operator, limit=limit)
