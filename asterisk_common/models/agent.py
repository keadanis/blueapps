# ©️ OdooPBX by Odooist, Odoo Proprietary License v1.0, 2020
from datetime import datetime, timedelta
import json
from jsonrpcclient.client import Client as JsonRpcClient
from jsonrpcclient.response import Response as JsonRpcResponse
from jsonrpcclient.exceptions import JsonRpcClientError
from jsonrpcclient.exceptions import ReceivedErrorResponseError
try:
    import humanize
    HUMANIZE = True
except ImportError:
    HUMANIZE = False
import logging
import os
import random
import requests
import string
import time
from urllib.parse import urlparse, urlunparse
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import uuid

from odoo import models, fields, api, registry, _, SUPERUSER_ID
from odoo.exceptions import ValidationError
from odoo.addons.bus.models.bus import dispatch

from .agent_state import STATES

logger = logging.getLogger(__name__)
logging.getLogger('jsonrpcclient').setLevel(logging.WARNING)

DEFAULT_PASSWORD_LENGTH = os.getenv('AGENT_DEFAULT_PASSWORD_LENGTH', '10')
CHANNEL_PREFIX = 'remote_agent'


class AgentError(Exception):
    def __init__(self, message, note=None):
        self.message = message
        self.note = note
        super().__init__(message)


class AgentClient(JsonRpcClient):

    def __init__(self, agent):
        self.agent = agent
        self.env = agent.env
        self.message = {
            'token': agent.token,
            'system_name': agent.system_name,
            'command': 'jsonrpc',
        }

    def send_message(self, request, response_expected, **kwargs):
        if self.agent.connection_type == 'bus':
            return self.send_bus_message(request, response_expected, **kwargs)
        elif self.agent.connection_type == 'http':
            return self.send_http_message(request, response_expected, **kwargs)
        else:
            raise AgentError(
                'Unknown connection method!')

    def update_state(self, state, note):
        if state == self.agent.state:
            # State did not change.
            return
        # Update agent state
        with api.Environment.manage():
            with registry(self.env.cr.dbname).cursor() as new_cr:
                env = api.Environment(
                    new_cr, SUPERUSER_ID, self.env.context)
                env['remote_agent.agent'].browse(
                    self.agent.id).update_state(
                    state=state, note=note)
                env.cr.commit()

    def send_bus_message(self, request, response_expected, **kwargs):
        channel = '{}/{}'.format(CHANNEL_PREFIX, self.agent.system_name)
        self.message['request'] = request
        reply_channel = '{}/{}'.format(channel, uuid.uuid4().hex)
        if response_expected:
            # Add reply channel
            self.message['reply_channel'] = reply_channel
        with api.Environment.manage():
            with registry(self.env.cr.dbname).cursor() as new_cr:
                env = api.Environment(new_cr, self.env.uid, self.env.context)
                env['bus.bus'].sendone(channel, json.dumps(self.message))
                new_cr.commit()
        # Request or notification?
        if not response_expected:
            # Notification
            return JsonRpcResponse('')
        # Request, wait for response.
        agent_reply = None
        # Poll is done in a separate transaction so we don't do it.
        if dispatch:
            # Gevent instance
            agent_reply = dispatch.poll(self.env.cr.dbname,
                                        [reply_channel],
                                        last=0,
                                        timeout=self.agent.bus_timeout)
        else:
            # Cron instance
            started = datetime.utcnow()
            to_end = started + timedelta(seconds=self.agent.bus_timeout)
            agent_reply = None
            while datetime.now() < to_end:
                with api.Environment.manage():
                    with registry(self.env.cr.dbname).cursor() as new_cr:
                        env = api.Environment(
                            new_cr, self.env.uid, self.env.context)
                        rec = env['bus.bus'].sudo().search(
                            [('create_date', '>=', started.strftime(
                                '%Y-%m-%d %H:%M:%S')),
                             ('channel', '=', '"{}"'.format(reply_channel))])
                        if not rec:
                            time.sleep(0.25)
                        else:
                            logger.debug(
                                'Got reply within %s seconds',
                                (datetime.now() - started).total_seconds()),
                            agent_reply = [{'message':
                                            json.loads(rec[0].message)}]
                            break
        if agent_reply:
            # Update agent state
            self.update_state('online',
                              '{} reply'.format(self.message['command']))
            # Convert result message to dict
            return JsonRpcResponse(agent_reply[0]['message'])
        # No reply recieved
        else:
            self.update_state(
                'offline', '{} not replied'.format(str(request)))
            raise AgentError('Offline')

    def send_http_message(self, request, response_expected, **kwargs):
        self.message['request'] = request
        try:
            r = requests.post(
                self.agent.http_url,
                timeout=self.agent.http_timeout,
                json=self.message,
                headers={
                    'X-Token': self.agent.token,
                    'Response-Expected': '1' if response_expected else '0',
                },
                verify=self.agent.http_ssl_verify)
            r.raise_for_status()
            self.update_state('online',
                              '{} reply'.format(self.message['command']))
            return JsonRpcResponse(r.text, raw=r)
        except Exception as e:
            logger.error('Agent HTTP error: %s', e)
            self.update_state('offline',
                '{} not replied: {}'.format(self.message['command'], str(e)))
            raise AgentError('Offline', note=str(e))


class Agent(models.Model):
    _name = 'remote_agent.agent'
    _description = 'Remote Agent'
    _rec_name = 'note'

    note = fields.Char(required=True, string='Name', default='Asterisk')
    system_name = fields.Char(readonly=True, required=True,
                              string='System ID',
                              default=lambda r: r._get_default_system_name())
    version = fields.Char(readonly=True)
    current_db = fields.Char(compute='_get_current_db', string='Database')
    alarm = fields.Text(readonly=True)
    token = fields.Char(default='never-connected')
    connection_type = fields.Selection([('bus', 'Bus'), ('http', 'HTTP(s)')],
                                       default='bus', required=True)
    bus_timeout = fields.Integer(default=10)
    http_url = fields.Char(string=_('HTTP(s) URL'),
                           default='https://127.0.0.1:40000')
    http_timeout = fields.Integer(string=_('HTTP(s) Timeout'), default=10)
    http_ssl_verify = fields.Boolean(string=_('SSL Verify'),
                                     help=_("Verify agent's certificate"))
    user = fields.Many2one('res.users', ondelete='restrict', required=True)
    tz = fields.Selection(related='user.tz', readonly=False)
    country_id = fields.Many2one(related='user.country_id', readonly=False)
    states = fields.One2many(comodel_name='remote_agent.agent_state',
                             inverse_name='agent')
    state_count = fields.Integer(compute='_get_state_count')
    state = fields.Selection(STATES, store=True, compute='_get_current_state')
    state_changed = fields.Datetime(compute='_get_state_changed')
    state_changed_human = fields.Char(compute='_get_state_changed_human',
                                      string=_('State Changed'))
    state_icon = fields.Char(compute='_get_state_changed_icon')
    last_online = fields.Datetime(compute='_get_last_online')
    last_online_human = fields.Char(compute='_get_last_online_human',
                                    string=_('Last Online'))

    _sql_constraints = [
        ('system_name_uniq', 'unique(system_name)',
            _('This system name already exists!')),
        ('user_uniq', 'unique("user")',
            _('This user is already used!')),
    ]

    def _get_default_system_name(self):
        return 'agent_not_connected'

    def _get_current_db(self):
        self.current_db = self.env.cr.dbname

    def open_agent_form(self):
        rec = self.env.ref('asterisk_common.remote_agent')
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'remote_agent.agent',
            'res_id': rec.id,
            'name': 'Agent',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'current',
        }

# Model and UI methods #

    def refresh_view_button(self):
        return True

    @api.depends('states')
    def _get_current_state(self):
        for rec in self:
            state_changed = self.env['remote_agent.agent_state'].search([
                ('agent', '=', rec.id)], limit=1, order='id desc')
            rec.state = state_changed[
                0].state if state_changed else 'offline'

    def _get_state_changed(self):
        for rec in self:
            state_changed = self.env['remote_agent.agent_state'].search([
                ('agent', '=', rec.id)], limit=1, order='id desc')
            rec.state_changed = state_changed[
                0].create_date if state_changed else False

    def _get_state_changed_human(self):
        global HUMANIZE
        if HUMANIZE:
            try:
                to_translate = self.env.context.get('lang', 'en_US')
                if to_translate != 'en_US':
                    humanize.i18n.activate(to_translate)
            except Exception:
                HUMANIZE = False
        for rec in self:
            state_changed = self.env['remote_agent.agent_state'].search([
                ('agent', '=', rec.id)], limit=1, order='id desc')
            if state_changed:
                if HUMANIZE:
                    rec.state_changed_human = humanize.naturaltime(
                        fields.Datetime.from_string(
                            state_changed[0].create_date))
                else:
                    rec.state_changed_human = state_changed[0].create_date
            else:
                rec.state_changed_human = ''

    def _get_state_changed_icon(self):
        for rec in self:
            if rec.state == 'online':
                rec.state_icon = '<span class="fa fa-chain"/>'
            else:
                rec.state_icon = '<span class="fa fa-chain-broken"/>'

    def _get_last_online(self):
        for rec in self:
            state_changed = self.env['remote_agent.agent_state'].search([
                ('agent', '=', rec.id), ('state', '=', 'online')],
                limit=1, order='id desc')
            rec.last_online = state_changed[0].create_date if \
                state_changed else False

    def _get_last_online_human(self):
        try:
            if HUMANIZE:
                to_translate = self.env.context.get('lang', 'en_US')
                if to_translate != 'en_US':
                    humanize.i18n.activate(to_translate)
            for rec in self:
                if HUMANIZE:
                    rec.last_online_human = humanize.naturaltime(
                        fields.Datetime.from_string(
                            rec.last_online)) if rec.last_online else ''
                else:
                    rec.last_online_human = rec.last_online
        except Exception:
            logger.exception('Humanize error:')
            for rec in self:
                rec.last_online_human = rec.last_online

    def _get_state_count(self):
        for rec in self:
            rec.state_count = len(rec.states)

    def generate_password(length=DEFAULT_PASSWORD_LENGTH):
        try:
            length = int(length)
        except ValueError:
            logger.warning('Bad DEFAULT_PASSWORD_LENGTH: %s',
                           DEFAULT_PASSWORD_LENGTH)
            length = 10
        chars = string.ascii_letters + string.digits
        password = ''
        while True:
            password = ''.join(map(lambda x: random.choice(
                chars), range(length)))
            if filter(lambda c: c.isdigit(), password) and \
                    filter(lambda c: c.isalpha(), password):
                break
        return password

    def adjust_permissions(self):
        self.ensure_one()
        # Set to Portal
        if not self.user.has_group(
                'base.group_portal'):
            # Reset user role
            self.user.write({'groups_id': [
                (3, self.env.ref('base.group_user').id),
                (4, self.env.ref('base.group_portal').id)
            ]})
        if not self.user.has_group('asterisk_common.group_asterisk_agent'):
            ast_group = self.env.ref('asterisk_common.group_asterisk_agent')
            ast_group.write({'users': [(4, self.user.id)]})

    @api.model
    def get_agent(self, system_name):
        agent = self.search([('system_name', '=', system_name)])
        if not agent:
            raise ValidationError('Agent {} not found!'.format(system_name))
        return agent

    def request(self, method, *args, **kwargs):
        self.ensure_one()
        client = AgentClient(self)
        try:
            response = client.request('execute', method, args, kwargs)
            return response.data.result
        except ReceivedErrorResponseError:
            raise AgentError('Server error')

    def notify(self, method, *args, **kwargs):
        self.ensure_one()
        client = AgentClient(self)
        return client.notify('execute', method, args, kwargs)

    def action(self, action, notify=False, **kwargs):
        self.ensure_one()
        if notify:
            return self.notify('asterisk.manager_action', action, **kwargs)
        else:
            return self.request('asterisk.manager_action', action, **kwargs)

    @api.model
    def reload_view(self, uid=None, model=None):
        if not uid:
            uid = self.env.uid
        self.env['bus.bus'].sendone(
            'remote_agent_notification_{}'.format(uid),
            {'reload': True, 'model': model})
        return True

    def reload_events(self):
        self.ensure_one()
        self.action({'Action': 'ReloadEvents'}, notify=True,
                    status_notify_uid=self.env.uid)

    def restart(self):
        self.ensure_one()
        client = AgentClient(self)
        # Overwritee json-rpc command
        client.message['command'] = 'restart'
        client.message['notify_uid'] = self.env.user.id
        client.notify('restart')
    
    def ping_agent(self):
        try:
            self.notify('test.ping', status_notify_uid=self.env.uid)
        except AgentError as e:
            raise ValidationError('Agent error: {}'.format(e))

    def ping_asterisk(self):
        self.ensure_one()
        try:
            res = self.action({'Action': 'Ping'})
        except AgentError as e:
            raise ValidationError('Agent error: {}'.format(e))
        self.env.user.asterisk_notify(res[0]['Response'])


    def clear_alarm_button(self):
        self.ensure_one()
        self.alarm = False

# RPC Calls from Agent #
    @api.model
    def bus_sendone(self, channel, message):
        # Override sendone as original method does not return value for RPC
        self.env['bus.bus'].sendone(channel, message)
        return True

    @api.model
    def update_token(self, token):
        agent = self.env.user.remote_agent
        if not agent:
            logger.error('Agent not found for user %s!', self.env.user)
            return False
        else:
            agent.token = token
            agent.update_state()
            return True

    @api.model
    def update_system_name(self, system_name, version):
        # Called from the Agent to set its system name before polling.
        agent = self.env.user.remote_agent
        if not agent:
            logger.error('Agent not found for user %s!', self.env.user.name)
            return False
        else:
            agent.write({
                'system_name': system_name,
                'version': version,
            })
            return True

    def update_state(self, state='online', note=False, force_create=False):
        # Method called from Agent to update its state on start.
        self.ensure_one()
        state_changed = self.env['remote_agent.agent_state'].search([
            ('agent', '=', self.id)], limit=1, order='id desc')
        # Create online state if previous state was offline
        if (force_create or not state_changed or
                (state_changed and state_changed.state != state)):
            self.env['remote_agent.agent_state'].create(
                {'agent': self.id, 'note': note, 'state': state})
        return True

    @api.model
    def set_alarm(self, system_name, message):
        agent = self.search([('system_name', '=', system_name)])
        agent.alarm = message
        return True

    @api.model
    def clear_alarm(self, system_name, message):
        # TODO: alarm message in event log
        agent = self.search([('system_name', '=', system_name)])
        agent.alarm = False
        return True
