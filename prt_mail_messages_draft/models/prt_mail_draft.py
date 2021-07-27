###################################################################################
# 
#    Copyright (C) Cetmix OÜ
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU LESSER GENERAL PUBLIC LICENSE as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###################################################################################

from odoo import models, fields, api, _, tools

# import logging
# _logger = logging.getLogger(__name__)


# -- Select draft
def _select_draft(draft):
    if draft:
        return {
            'name': _("New message"),
            "views": [[False, "form"]],
            'res_model': 'mail.compose.message',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_res_id': draft.res_id,
                'default_model': draft.model,
                'default_parent_id': draft.parent_id,
                'default_partner_ids': draft.partner_ids.ids or False,
                'default_attachment_ids': draft.attachment_ids.ids or False,
                'default_is_log': False,
                'default_subject': draft.subject,
                'default_body': draft.body,
                'default_subtype_id': draft.subtype_id.id,
                'default_message_type': 'comment',
                'default_current_draft_id': draft.id,
                'default_signature_location': draft.signature_location,
                'default_wizard_mode': draft.wizard_mode
                }
        }


######################
# Mail.Message.Draft #
######################
class PRTMailMessageDraft(models.Model):
    _name = "prt.mail.message.draft"
    _description = "Draft Message"
    _order = 'write_date desc, id desc'
    _rec_name = 'subject'

# -- Set domain for subtype_id
    def _get_subtypes(self):
        return [('id', 'in', [self.env['ir.model.data'].xmlid_to_res_id('mail.mt_comment'),
                              self.env['ir.model.data'].xmlid_to_res_id('mail.mt_note')])]

    subject = fields.Char(string="Subject")
    subject_display = fields.Char(string="Subject", compute="_subject_display")
    body = fields.Html(string="Contents", default="", sanitize_style=True, strip_classes=True)

    model = fields.Char(sting="Related Document Model", index=True)
    res_id = fields.Integer(string="Related Document ID", index=True)

    subtype_id = fields.Many2one(string="Message Type", comodel_name='mail.message.subtype',
                                 domain=_get_subtypes,
                                 default=lambda self: self.env['ir.model.data'].xmlid_to_res_id('mail.mt_comment'),
                                 required=True)
    parent_id = fields.Integer(string="Parent Message")
    author_id = fields.Many2one(string="Author", comodel_name='res.partner', index=True,
                                ondelete='set null',
                                default=lambda self: self.env.user.partner_id.id)
    partner_ids = fields.Many2many(string="Recipients", comodel_name='res.partner')
    record_ref = fields.Reference(string="Message Record", selection='_referenceable_models',
                                  compute='_record_ref')
    attachment_ids = fields.Many2many(string="Attachments", comodel_name='ir.attachment',
                                      relation='prt_message_draft_attachment_rel',
                                      column1='message_id',
                                      column2='attachment_id')

    ref_partner_ids = fields.Many2many(string="Followers", comodel_name='res.partner',
                                       compute='_message_followers')
    ref_partner_count = fields.Integer(string="Followers", compute='_ref_partner_count')
    wizard_mode = fields.Char(string="Wizard Mode", default='composition')
    signature_location = fields.Selection([
        ('b', 'Before quote'),
        ('a', 'Message bottom'),
        ('n', 'No signature')
    ], string='Signature Location', default='b', required=True,
        help='Whether to put signature before or after the quoted text.')

# -- Count ref Partners
    def _ref_partner_count(self):
        for rec in self:
            rec.ref_partner_count = len(rec.ref_partner_ids)

# -- Get related record followers
    @api.depends('record_ref')
    def _message_followers(self):
        for rec in self:
            if rec.record_ref:
                rec.ref_partner_ids = rec.record_ref.message_partner_ids

# -- Get Subject for tree view
    @api.depends('subject')
    def _subject_display(self):

        # Get model names first. Use this method to get translated values
        ir_models = self.env['ir.model'].search([('model', 'in', list(set(self.mapped('model'))))])
        model_dict = {}
        for model in ir_models:
            # Check if model has "name" field
            has_name = self.env['ir.model.fields'].sudo().search_count([('model_id', '=', model.id),
                                                                        ('name', '=', 'name')])
            model_dict.update({model.model: [model.name, has_name]})

        # Compose subject
        for rec in self:
            subject_display = '=== No Reference ==='

            # Has reference
            if rec.record_ref:
                subject_display = model_dict.get(rec.model)[0]

                # Has 'name' field
                if model_dict.get(rec.model, False)[1]:
                    subject_display = "%s: %s" % (subject_display, rec.record_ref.name)

                # Has subject
                if rec.subject:
                    subject_display = "%s => %s" % (subject_display, rec.subject)

            # Set subject
            rec.subject_display = subject_display

# -- Ref models
    @api.model
    def _referenceable_models(self):
        return [(x.model, x.name) for x in self.env['ir.model'].sudo().search([('model', '!=', 'mail.channel')])]

# -- Compose reference
    @api.depends('res_id')
    def _record_ref(self):
        for rec in self:
            if rec.res_id:
                if rec.model:
                    res = self.env[rec.model].sudo().search([("id", "=", rec.res_id)])
                    if res:
                        rec.record_ref = res

# -- Send message
    def send_it(self):
        self.ensure_one()

        # Compose message body
        return _select_draft(self)


###############
# Mail.Thread #
###############
class PRTMailThread(models.AbstractModel):
    _name = "mail.thread"
    _inherit = "mail.thread"

# -- Unlink: delete all drafts
    def unlink(self):
        if not self._name == 'prt.mail.message.draft':
            self.env['prt.mail.message.draft'].sudo().search([('model', '=', self._name),
                                                              ('id', 'in', self.ids)]).sudo().unlink()
        return super().unlink()
    

########################
# Mail.Compose Message #
########################
class PRTMailComposer(models.TransientModel):
    _inherit = 'mail.compose.message'
    _name = 'mail.compose.message'

    current_draft_id = fields.Many2one(string="Draft", comodel_name='prt.mail.message.draft')

# -- Save draft wrapper
    def _save_draft(self, draft):
        self.ensure_one()

        if draft:
            # Update existing draft
            res = draft.write({
                'res_id': self.res_id,
                'model': self.model,
                'parent_id': self.parent_id.id,
                'author_id': self.author_id.id,
                'partner_ids': [(6, False, self.partner_ids.ids)],
                'attachment_ids': [(6, False, self.attachment_ids.ids)],
                'subject': self.subject,
                'signature_location': self.signature_location,
                'body': self.body,
                'wizard_mode': self.wizard_mode,
                'subtype_id': self.subtype_id.id,
            })

        else:
            # Create new draft
            res = self.env['prt.mail.message.draft'].create({
                'res_id': self.res_id,
                'model': self.model,
                'parent_id': self.parent_id.id,
                'author_id': self.author_id.id,
                'partner_ids': [(4, x, False) for x in self.partner_ids.ids],
                'attachment_ids': [(4, x, False) for x in self.attachment_ids.ids],
                'subject': self.subject,
                'signature_location': self.signature_location,
                'wizard_mode': self.wizard_mode,
                'body': self.body,
                'subtype_id': self.subtype_id.id,
            })

        return res

# -- Save draft button
    def save_draft(self):

        # Save or create draft
        res = self._save_draft(self.current_draft_id)

        # If just save
        if self._context.get('save_mode', False) == 'save':
            # Reopen current draft
            if self.current_draft_id:
                return _select_draft(self.current_draft_id)

            # .. or newly created
            return _select_draft(res)

        # If in 'compose mode'
        if self.wizard_mode == 'compose':
            return self.env['ir.actions.act_window'].for_xml_id('prt_mail_messages_draft',
                                                                'action_prt_mail_messages_draft')

        return

# -- Override send
    def send_mail(self, auto_commit=False):

        # Send message
        res = super().send_mail(auto_commit=auto_commit)

        # Delete drafts modified by current user
        self.env['prt.mail.message.draft'].sudo().search([('model', '=', self.model),
                                                          ('res_id', '=', self.res_id),
                                                          ('write_uid', '=', self.create_uid.id)]).sudo().unlink()

        # If in 'compose mode'
        if self._context.get('wizard_mode', False) == 'compose':
            res = self.env['ir.actions.act_window'].for_xml_id('prt_mail_messages', 'action_prt_mail_messages')

        return res
