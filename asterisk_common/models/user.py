# ©️ OdooPBX by Odooist, Odoo Proprietary License v1.0, 2020
import logging
from odoo import models, fields, api, tools, _, SUPERUSER_ID
from odoo.exceptions import ValidationError
import uuid

logger = logging.getLogger(__name__)

# Fields allowed to be changed by user.
USER_PERMITTED_FIELDS = [
    'originate_vars', 'channels', 'originate_enabled', 'auto_answer_header',
]

AUTO_ANSWER_HEADERS = [
    ('Alert-Info: Info=Alert-Autoanswer', 'Alert-Info: Info=Alert-Autoanswer'),
    ('Alert-Info: Info=Auto Answer', 'Alert-Info: Info=Auto Answer'),
    ('Alert-Info: ;info=alert-autoanswer', 'Alert-Info: ;info=alert-autoanswer'),
    ('Alert-Info: <sip:>;info=alert-autoanswer', 'Alert-Info: <sip:>;info=alert-autoanswer'),
    ('Alert-Info: Ring Answer', 'Alert-Info: Ring Answer'),
    ('Answer-Mode: Auto', 'Answer-Mode: Auto'),
    ('Call Info: Answer-After=0', 'Call Info: Answer-After=0'),
    ('Call-Info: <sip:>;answer-after=0', 'Call-Info: <sip:>;answer-after=0'),
    ('P-Auto-Answer: normal', 'P-Auto-Answer: normal'),
]


class AsteriskUserChannel(models.Model):
    _name = 'asterisk_common.user_channel'
    _rec_name = 'channel'
    _description = 'Asterisk User Channel'

    sequence = fields.Integer(default=100, index=True)
    channel = fields.Char(required=True)
    # Store originate_context here.
    context = fields.Char()
    asterisk_user = fields.Many2one('asterisk_common.user', required=True,
                                    ondelete='cascade')
    user = fields.Many2one(related='asterisk_user.user', readonly=True)
    agent = fields.Many2one(related='asterisk_user.agent', readonly=True)
    system_name = fields.Char(related='asterisk_user.agent.system_name',
                              readonly=True, store=True)
    originate_enabled = fields.Boolean(default=True, string="Originate")
    originate_context = fields.Char(
        default=lambda self: self._get_default_context(),
        string='Context',
        compute='_get_originate_context', inverse='_set_originate_context')
    auto_answer_header = fields.Selection(AUTO_ANSWER_HEADERS)

    _sql_constraints = [
        ('system_channel_uniq', 'unique (system_name,channel)',
            _('The channel is already defined for this System!')),
    ]

    def write(self, values):
        if not (self.env.user.has_group(
                'asterisk_common.group_asterisk_admin') or
                self.env.user.id == SUPERUSER_ID):
            # User can only change some fields.
            restricted_fields = set(values.keys()) - set(USER_PERMITTED_FIELDS)
            if restricted_fields:
                raise ValidationError(
                    _('Fields {} not allowed to be changed!').format(
                        restricted_fields))
        res = super(AsteriskUserChannel, self).write(values)
        return res

    @api.constrains('channel')
    def _check_channel_name(self):
        for rec in self:
            try:
                chan, name = rec.channel.split('/')
            except ValueError:
                raise ValidationError(
                    _('Bad channel format. Example: SIP/101.'))

    def _get_default_context(self):
        return self.env['asterisk_common.settings'].get_param(
            'originate_context', 'from-internal')

    def _get_originate_context(self):
        for rec in self:
            rec.originate_context = rec.context

    def _set_originate_context(self):
        for rec in self:
            rec.context = rec.originate_context


class AsteriskUser(models.Model):
    _name = 'asterisk_common.user'
    _order = 'user'
    _rec_name = 'user'
    _description = _('Asterisk User')

    exten = fields.Char()
    user = fields.Many2one('res.users', required=True,
                           ondelete='cascade',
                           # Exclude shared users
                           domain=[('share', '=', False)])
    name = fields.Char(related='user.name', readonly=True)
    agent = fields.Many2one('remote_agent.agent', string='System',
                            required=True, ondelete='restrict',
                            default=lambda self: self._get_default_agent())
    system_name = fields.Char(related='agent.system_name', store=True)
    partner = fields.Many2one(related='user.partner_id', readonly=True)
    is_primary_system = fields.Boolean(default=True, string='Primary')
    channels = fields.One2many('asterisk_common.user_channel',
                               inverse_name='asterisk_user')
    originate_vars = fields.Text(string='Channel Variables')

    _sql_constraints = [
        ('exten_uniq', 'unique (exten,agent)',
         _('This phone extension is already used!')),
        ('user_uniq', 'unique ("user",agent)',
         _('This user is already defined!')),
        ('primary_uniq', 'unique ("user",is_primary_system)',
         _('The primary system is already defined!')),
    ]

    @api.model
    def create(self, vals):
        user = super(AsteriskUser, self).create(vals)
        if not user.user.has_group('asterisk_common.group_asterisk_user') and \
                not user.user.has_group('asterisk_common.group_asterisk_admin'):
            # First time adding Odoo user to PBX user, so add also Asterisk User group.
            asterisk_user_group = self.env.ref(
                'asterisk_common.group_asterisk_user')
            asterisk_user_group.sudo().users = [(4, user.user.id)]
        if user and not self.env.context.get('no_clear_cache'):
            self.pool.clear_caches()
        return user

    def write(self, values):
        if not (self.env.user.has_group(
                'asterisk_common.group_asterisk_admin') or
                self.env.user.id == SUPERUSER_ID):
            # User can only change some fields.
            restricted_fields = set(values.keys()) - set(USER_PERMITTED_FIELDS)
            if restricted_fields:
                raise ValidationError(
                    _('Fields {} not allowed to be changed!').format(
                        restricted_fields))
        res = super(AsteriskUser, self).write(values)
        if res and not self.env.context.get('no_clear_cache'):
            self.pool.clear_caches()
        # Automatically apply changes for user
        if not (self.env.user.has_group(
                'asterisk_common.group_asterisk_admin') or
                self.env.user.id == SUPERUSER_ID):
            if not self.env.user.asterisk_user:
                raise ValidationError('PBX user is not defined!')
            self.env.user.asterisk_user.server.sudo().with_context(
                disable_notify=True).apply_changes()
        return res

    def unlink(self):
        res = super(AsteriskUser, self).unlink()
        if res and not self.env.context.get('no_clear_cache'):
            self.pool.clear_caches()
        return res

    @api.model
    def has_asterisk_group(self):
        if (self.env.user.has_group('asterisk_common.group_asterisk_user') or
                self.env.user.has_group(
                'asterisk_common.group_asterisk_admin')):
            return True

    def _get_default_agent(self):
        agents = self.env['remote_agent.agent'].search([])
        if len(agents) == 1:
            return agents[0].id

    def open_user_form(self):
        if self.env.user.has_group('asterisk_common.group_asterisk_admin'):
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'asterisk_common.user',
                'name': 'Users',
                'view_mode': 'tree,form',
                'view_type': 'form',
                'target': 'current',
            }
        else:
            if not self.env.user.asterisk_user:
                raise ValidationError('PBX user is not configured!')
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'asterisk_common.user',
                'res_id': self.env.user.asterisk_user.id,
                'name': 'User',
                'view_id': self.env.ref(
                    'asterisk_common.asterisk_user_user_form').id,
                'view_mode': 'form',
                'view_type': 'form',
                'target': 'current',
            }

    def _get_originate_vars(self):
        self.ensure_one()
        try:
            if not self.originate_vars:
                return []
            return [k for k in self.originate_vars.split('\n') if k]
        except Exception:
            logger.exception('Get originate vars error:')
            return []

    def dial_user(self):
        self.ensure_one()
        self.originate_call(self.exten)

    @api.model
    def originate_call(self, number, model=None, res_id=None,
                       system_name='asterisk'):
        if not number:
            raise ValidationError(_('Phone number not set!'))
        if not self.env.user.asterisk_user:
            raise ValidationError(_("PBX user is not configured!"))
        format_type = self.env['asterisk_common.settings'].get_param(
            'originate_format', 'e164')
        # Format number if required
        if format_type != 'no_format' and model and res_id:
            logger.debug('FORMAT NUMBER FOR MODEL %s', model)
            obj = self.env[model].browse(res_id)
            if getattr(obj, '_format_number', False):
                number = obj._format_number(number, format_type=format_type)
                logger.debug('MODEL FORMATTED NUMBER: {}'.format(number))
        else:
            logger.debug('FORMAT NOT ENABLED')
        # Strip formatting if present
        number = number.replace(' ', '')
        number = number.replace('(', '')
        number = number.replace(')', '')
        number = number.replace('-', '')
        if number[0] == '+' and self.env['asterisk_common.settings'].get_param(
                'originate_strip_plus'):
            logger.debug('REMOVING +')
            number = number[1:]
        prefix = self.env['asterisk_common.settings'].get_param(
            'originate_prefix')
        if prefix:
            logger.debug('ADDING ORIGINATE PREFIX %s', prefix)
            number = '{}{}'.format(prefix, number)
        logger.debug('ORIGINATE NUMBER %s', number)
        # Get user defined varaibles headers for auto-answer.
        variables = self.env.user.asterisk_user._get_originate_vars()
        # Set callerid to dialed partner if set in options
        if self.env['asterisk_common.settings'].get_param(
                'originate_partner_callerid'):
            # Save original callerid
            variables.append('OUTBOUND_CALLERID="{}" <{}>'.format(
                self.env.user.name, self.env.user.asterisk_user.exten))
            if model and res_id:
                obj = self.env[model].browse(res_id)
                if hasattr(obj, 'name'):
                    name = obj.name
                else:
                    name = number
                callerid = 'To: {} <{}>'.format(name, number)
            else:
                callerid = 'To: {} <{}>'.format(number, number)
        # Get originate timeout
        originate_timeout = float(self.env[
            'asterisk_common.settings'].get_param('originate_timeout'))
        # Check if user has channels
        if not self.env.user.asterisk_user.channels:
            raise ValidationError('You do not have any channels set up!')
        originate_channels = [k for k in self.env.user.asterisk_user.channels
                              if k.originate_enabled]
        if not originate_channels:
            raise ValidationError(
                _('Enable at least one channel to originate!'))
        # Init channel_ids for all channels to populate originate_channels
        originate_channels_data = {}
        for ch in originate_channels:
            originate_channels_data[ch.channel] = {
                'channel_id': uuid.uuid4().hex,
                'other_channel_id': uuid.uuid4().hex,
            }
        for user_channel in originate_channels:
            # Save in cache originate operation
            channel_id = originate_channels_data[
                user_channel.channel]['channel_id']
            channel_vars = variables.copy()
            if user_channel.auto_answer_header:
                header = user_channel.auto_answer_header
                try:
                    pos = header.find(':')
                    param = header[:pos]
                    val = header[pos+1:]
                    if 'PJSIP' in user_channel.channel.upper():
                        channel_vars.append(
                            'PJSIP_HEADER(add,{})={}'.format(
                                param.lstrip(), val.lstrip()))
                    else:
                        channel_vars.append(
                            'SIPADDHEADER={}: {}'.format(
                                param.lstrip(), val.lstrip()))
                except Exception:
                    logger.warning(
                        'Cannot parse auto answer header: %s', header)
            originate_call_data = {
                'uid': self.env.user.id,
                'channel': channel_id,
                'model': model,
                'res_id': res_id,
                'originate_timeout': originate_timeout,
                'originate_channels': originate_channels_data,
            }
            self.env['kv_cache.cache'].put(
                channel_id, originate_call_data, tag='originated_call',
                serialize='json', new_env=True)
            self.call_originate_request(
                system_name=self.env.user.asterisk_user.agent.system_name,
                exten=self.env.user.asterisk_user.exten,
                context=user_channel.originate_context,
                number=number,
                channel=user_channel.channel,
                channel_id=channel_id,
                other_channel_id=originate_channels_data[
                    user_channel.channel]['other_channel_id'],
                callerid=callerid,
                timeout=originate_timeout,
                variables=channel_vars)

    @api.model
    def call_originate_request(self, system_name='asterisk', exten=None,
                               context=None, number=None, channel=None,
                               channel_id=None, other_channel_id=None,
                               variables=[], callerid='"" <>', timeout=None):
        # Generate channel ID to track it.
        if not channel_id:
            channel_id = uuid.uuid4().hex
        if not other_channel_id:
            other_channel_id = uuid.uuid4().hex
        if not timeout:
            timeout = int(self.env[
                    'asterisk_common.settings'].get_param(
                    'originate_timeout'))
        self.env.user.asterisk_user.agent.action({
            'Action': 'Originate',
            'Context': context,
            'Priority': '1',
            'Timeout': 1000 * timeout,
            'Channel': channel,
            'Exten': number,
            'Async': 'true',
            'EarlyMedia': 'true',
            'CallerID': callerid,
            'ChannelId': channel_id,
            'OtherChannelId': uuid.uuid4().hex,
            'Variable': variables,
            },
            passback={'uid': self.env.user.id},
            callback=('asterisk_common.user', 'call_originate_response'),
        )

    @api.model
    def call_originate_response(self, data):
        result = data.get('result') and data['result'][0]
        uid = data.get('passback', {}).get('uid', 0)
        if result:
            if result['Response'] == 'Error' and uid:
                message = result['Message']
                self.env.user.asterisk_notify(message, uid=uid, warning=True)
                logger.warning('ORIGINATE ERROR: %s', message)
        elif data.get('error') and uid:
            message = data['error'].get('message') or str(data['error'])
            self.env.user.asterisk_notify(message, uid=uid, warning=True)
            logger.warning('ORIGINATE ERROR: %s', message)
        return True

    @api.model
    def ami_originate_response(self, data):
        # This comes from Asterisk OriginateResponse AMI message when
        # call originate has been failed.
        resp = data.get('Response')
        reason = data.get('Reason')
        uniqueid = data.get('Uniqueid')
        originate_data = self.env['kv_cache.cache'].get(
            uniqueid, tag='originated_call', serialize='json')
        originate_uid = originate_data.get('uid')
        if resp == 'Failure' and originate_uid:
            self.env['res.users'].asterisk_notify(
                _('Call failed, reason {0}').format(reason),
                uid=originate_uid, warning=True)
            logger.warning('ORIGINATE RESPONSE: %s', reason)
        return True
