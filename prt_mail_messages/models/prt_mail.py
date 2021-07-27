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

import logging
import threading
from datetime import datetime
from email.utils import parseaddr

import pytz

from odoo import SUPERUSER_ID, _, api, fields, models, registry
from odoo.exceptions import AccessError
from odoo.osv import expression
from odoo.tools import html2plaintext
from odoo.tools.misc import split_every

from .common import DEFAULT_MESSAGE_PREVIEW_LENGTH, IMAGE_PLACEHOLDER, MONTHS

# Used to render html field in TreeView
TREE_TEMPLATE = (
    '<table style="width:100%%;border:none;%s" title="%s">'
    "<tbody>"
    "<tr>"
    '<td style="width: 1%%;"><img class="rounded-circle"'
    ' style="width: 64px; padding:10px;" src="data:image/png;base64,%s"'
    ' alt="Avatar" title="%s" width="100" border="0" /></td>'
    '<td style="width: 99%%;">'
    '<table style="width: 100%%; border: none;">'
    "<tbody>"
    "<tr>"
    '<td id="author"><strong>%s</strong> &nbsp; <span id="subject">%s</span></td>'
    '<td id="date" style="text-align:right;"><span title="%s" id="date">%s</span></td>'
    "</tr>"
    "<tr>"
    "<td>"
    '<p id="related-record" style="font-size: x-small;"><strong>%s</strong></p></td>'
    '<td id="notifications" style="text-align: right;">%s</td>'
    "</tr>"
    "</tbody>"
    "</table>"
    '<p id="text-preview" style="color: #808080;">%s</p>'
    "</td>"
    "</tr>"
    "</tbody>"
    "</table>"
)

_logger = logging.getLogger(__name__)

TREE_VIEW_ID = False
FORM_VIEW_ID = False

# List of forbidden models
FORBIDDEN_MODELS = ["mail.channel"]

# Search for 'ghost' models is performed
GHOSTS_CHECKED = False


#############
# Mail.Mail #
#############
class MailMail(models.Model):
    _inherit = "mail.mail"

    # -- Post process sent mail messages
    def _postprocess_sent_message(
        self, success_pids, failure_reason=False, failure_type=None
    ):
        # Save messages to be deleted.
        # Mark them as NOT auto delete because we want to delete them via messages
        mail_to_delete_ids = [mail.id for mail in self if mail.auto_delete]
        if len(mail_to_delete_ids) > 0:
            mark_to_delete = self.sudo().browse(mail_to_delete_ids)
            mark_to_delete.write({"auto_delete": False})

        res = super(MailMail, self)._postprocess_sent_message(
            success_pids, failure_reason, failure_type
        )

        # Delete related messages so they will trigger
        # cascade mail.mail deletion
        if len(mail_to_delete_ids) > 0:
            mark_to_delete.write({"is_mail_mail": True})
            mark_to_delete.unlink()

        return res


###############
# Mail.Thread #
###############
class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    # -- Add context to unlink
    def unlink(self):
        return super(MailThread, self.with_context(force_delete=True)).unlink()

    # -- Notify partner
    def _notify_record_by_email(
        self,
        message,
        recipients_data,
        msg_vals=False,
        model_description=False,
        mail_auto_delete=True,
        check_existing=False,
        force_send=True,
        send_after_commit=True,
        **kwargs
    ):

        """
        Using Odoo generic method. Must keep an eye on changes
        """

        # Cetmix. Sent from Messages Easy composer?
        if not self._context.get("default_wizard_mode", False) in ["quote", "forward"]:
            return super(MailThread, self)._notify_record_by_email(
                message,
                recipients_data,
                msg_vals,
                model_description,
                mail_auto_delete,
                check_existing,
                force_send,
                send_after_commit,
                **kwargs
            )
        # Cetmix. Get signature location
        signature_location = self._context.get("signature_location", False)
        if signature_location == "a":  # Regular signature location
            return super(MailThread, self)._notify_record_by_email(
                message,
                recipients_data,
                msg_vals,
                model_description,
                mail_auto_delete,
                check_existing,
                force_send,
                send_after_commit,
                **kwargs
            )

        partners_data = [
            r for r in recipients_data["partners"] if r["notif"] == "email"
        ]
        if not partners_data:
            return True

        model = msg_vals.get("model") if msg_vals else message.model
        model_name = model_description or (
            self._fallback_lang().env["ir.model"]._get(model).display_name
            if model
            else False
        )  # one query for display name
        recipients_groups_data = self._notify_classify_recipients(
            partners_data, model_name
        )

        if not recipients_groups_data:
            return True
        force_send = self.env.context.get("mail_notify_force_send", force_send)

        template_values = self._notify_prepare_template_context(
            message, msg_vals, model_description=model_description
        )  # 10 queries
        # Cetmix. Replace signature
        if signature_location:  # Remove signature, we don't need it in values
            signature = template_values.pop("signature", False)
        else:
            signature = False

        email_layout_xmlid = (
            msg_vals.get("email_layout_xmlid")
            if msg_vals
            else message.email_layout_xmlid
        )
        template_xmlid = (
            email_layout_xmlid
            if email_layout_xmlid
            else "mail.message_notification_email"
        )
        try:
            base_template = self.env.ref(
                template_xmlid, raise_if_not_found=True
            ).with_context(
                lang=template_values["lang"]
            )  # 1 query
        except ValueError:
            _logger.warning(
                "QWeb template %s not found when sending notification emails."
                " Sending without layout." % (template_xmlid)
            )
            base_template = False

        mail_subject = message.subject or (
            message.record_name and "Re: %s" % message.record_name
        )  # in cache, no queries
        # prepare notification mail values
        base_mail_values = {
            "mail_message_id": message.id,
            "mail_server_id": message.mail_server_id.id,
            # 2 query, check acces + read, may be useless, Falsy, when will it be used?
            "auto_delete": mail_auto_delete,
            # due to ir.rule, user have no right to access parent message
            # if message is not published
            "references": message.parent_id.sudo().message_id
            if message.parent_id
            else False,
            "subject": mail_subject,
        }
        base_mail_values = self._notify_by_email_add_values(base_mail_values)

        Mail = self.env["mail.mail"].sudo()
        emails = self.env["mail.mail"].sudo()

        notif_create_values = []
        recipients_max = 50
        for recipients_group_data in recipients_groups_data:
            # generate notification email content
            recipients_ids = recipients_group_data.pop("recipients")
            render_values = {**template_values, **recipients_group_data}

            if base_template:
                mail_body = base_template._render(
                    render_values, engine="ir.qweb", minimal_qcontext=True
                )
            else:
                mail_body = message.body

            # Cetmix. Put signature before quote?
            if signature and signature_location == "b":
                quote_index = mail_body.find(b"<blockquote")
                if quote_index:
                    mail_body = (
                        mail_body[:quote_index]
                        + signature.encode("utf-8")
                        + mail_body[quote_index:]
                    )

            mail_body = self.env["mail.render.mixin"]._replace_local_links(mail_body)

            # create email
            for recipients_ids_chunk in split_every(recipients_max, recipients_ids):
                recipient_values = self._notify_email_recipient_values(
                    recipients_ids_chunk
                )
                email_to = recipient_values["email_to"]
                recipient_ids = recipient_values["recipient_ids"]

                create_values = {
                    "body_html": mail_body,
                    "subject": mail_subject,
                    "recipient_ids": [(4, pid) for pid in recipient_ids],
                }
                if email_to:
                    create_values["email_to"] = email_to
                create_values.update(
                    base_mail_values
                )  # mail_message_id, mail_server_id, auto_delete, references, headers
                email = Mail.create(create_values)

                if email and recipient_ids:
                    tocreate_recipient_ids = list(recipient_ids)
                    if check_existing:
                        existing_notifications = (
                            self.env["mail.notification"]
                            .sudo()
                            .search(
                                [
                                    ("mail_message_id", "=", message.id),
                                    ("notification_type", "=", "email"),
                                    ("res_partner_id", "in", tocreate_recipient_ids),
                                ]
                            )
                        )
                        if existing_notifications:
                            tocreate_recipient_ids = [
                                rid
                                for rid in recipient_ids
                                if rid
                                not in existing_notifications.mapped(
                                    "res_partner_id.id"
                                )
                            ]
                            existing_notifications.write(
                                {"notification_status": "ready", "mail_id": email.id}
                            )
                    notif_create_values += [
                        {
                            "mail_message_id": message.id,
                            "res_partner_id": recipient_id,
                            "notification_type": "email",
                            "mail_id": email.id,
                            "is_read": True,  # discard Inbox notification
                            "notification_status": "ready",
                        }
                        for recipient_id in tocreate_recipient_ids
                    ]
                emails |= email

        if notif_create_values:
            self.env["mail.notification"].sudo().create(notif_create_values)

        # NOTE:
        #   1. for more than 50 followers, use the queue system
        #   2. do not send emails immediately if the registry is not loaded,
        #      to prevent sending email during a simple update of the database
        #      using the command-line.
        test_mode = getattr(threading.currentThread(), "testing", False)
        if (
            force_send
            and len(emails) < recipients_max
            and (not self.pool._init or test_mode)
        ):
            # unless asked specifically, send emails after the transaction to
            # avoid side effects due to emails being sent while the transaction fails
            if not test_mode and send_after_commit:
                email_ids = emails.ids
                dbname = self.env.cr.dbname
                _context = self._context

                @self.env.cr.postcommit.add
                def send_notifications():
                    db_registry = registry(dbname)
                    with api.Environment.manage(), db_registry.cursor() as cr:
                        env = api.Environment(cr, SUPERUSER_ID, _context)
                        env["mail.mail"].browse(email_ids).send()

            else:
                emails.send()

        return True


################
# Mail.Message #
################
class MailMessage(models.Model):
    _inherit = "mail.message"

    author_display = fields.Char(string="Author", compute="_compute_author_display")

    # Fields to avoid access check issues
    author_allowed_id = fields.Many2one(
        string="Author",
        comodel_name="res.partner",
        compute="_compute_author_allowed",
        search="_search_author_allowed",
    )

    partner_allowed_ids = fields.Many2many(
        string="Recipients",
        comodel_name="res.partner",
        compute="_compute_partners_allowed",
    )
    attachment_allowed_ids = fields.Many2many(
        string="Attachments",
        comodel_name="ir.attachment",
        compute="_compute_attachments_allowed",
    )
    subject_display = fields.Html(string="Subject", compute="_compute_subject_display")
    partner_count = fields.Integer(
        string="Recipients count", compute="_compute_partner_count"
    )
    record_ref = fields.Reference(
        string="Message Record",
        selection="_referenceable_models",
        compute="_compute_record_ref",
    )
    attachment_count = fields.Integer(
        string="Attachments count", compute="_compute_attachment_count"
    )
    thread_messages_count = fields.Integer(
        string="Messages in thread",
        compute="_compute_thread_messages_count",
        help="Total number of messages in thread",
    )
    ref_partner_ids = fields.Many2many(
        string="Followers",
        comodel_name="res.partner",
        compute="_compute_message_followers",
    )
    ref_partner_count = fields.Integer(
        string="Followers", compute="_compute_ref_partner_count"
    )
    model_name = fields.Char(string="Model", compute="_compute_model_name")
    shared_inbox = fields.Boolean(
        string="Shared Inbox",
        compute="_compute_dummy",
        help="Used for Shared Inbox filter only",
        search="_search_shared_inbox",
    )
    cx_edit_uid = fields.Many2one(string="Edited by", comodel_name="res.users")
    cx_edit_date = fields.Datetime(string="Edited on")
    cx_edit_message = fields.Char(
        string="Edited by", compute="_compute_cx_edit_message"
    )
    # Used to distinguish mail.mail from mail.message. Used for unlink
    is_mail_mail = fields.Boolean()

    # -- Compute text shown as last edit message
    @api.depends("cx_edit_uid")
    def _compute_cx_edit_message(self):
        # Get current timezone
        tz = self.env.user.tz
        if tz:
            local_tz = pytz.timezone(tz)
        else:
            local_tz = pytz.utc

        # Get current time
        now = datetime.now(local_tz)

        # Check messages
        for rec in self:
            if not rec.cx_edit_uid:
                rec.cx_edit_message = False
                continue

            # Get message date with timezone
            message_date = pytz.utc.localize(rec.cx_edit_date).astimezone(local_tz)
            # Compose displayed date/time
            days_diff = (now.date() - message_date.date()).days
            if days_diff == 0:
                date_display = datetime.strftime(message_date, "%H:%M")
            elif days_diff == 1:
                date_display = " ".join(
                    (_("Yesterday"), datetime.strftime(message_date, "%H:%M"))
                )
            elif now.year == message_date.year:
                date_display = " ".join(
                    (str(message_date.day), _(MONTHS.get(message_date.month)))
                )
            else:
                date_display = str(message_date.date())
            rec.cx_edit_message = _("Edited by %s %s") % (
                rec.cx_edit_uid.name,
                date_display,
            )

    # -- Star several messages
    def mark_read_multi(self):
        for rec in self:
            if rec.needaction:
                rec.set_message_done()
            if rec.parent_id and rec.parent_id.needaction:
                rec.parent_id.set_message_done()

    # -- Star several messages
    def star_multi(self):
        for rec in self:
            rec.toggle_message_starred()

    # -- Search private inbox
    def _search_shared_inbox(self, operator, operand):
        if operator == "=" and operand:
            return [
                "|",
                ("author_id", "=", False),
                ("author_id", "!=", self.env.user.partner_id.id),
            ]
        return [("author_id", "!=", False)]

    # -- Get model name for Form View
    def _compute_model_name(self):
        ir_models = (
            self.env["ir.model"]
            .sudo()
            .search([("model", "in", list(set(self.mapped("model"))))])
        )
        model_dict = {}
        for model in ir_models:
            model_dict.update({model.model: model.name})
        for rec in self:
            rec.model_name = model_dict[rec.model] if rec.model else _("Lost Message")

    # -- Create
    @api.model
    def create(self, vals):

        # Update last message date if posting to Conversation
        message = super(MailMessage, self).create(vals)
        if (
            self._name == "mail.message"
            and message.model == "cetmix.conversation"
            and message.message_type != "notification"
        ):
            self.env["cetmix.conversation"].browse(message.res_id).update(
                {
                    "last_message_post": message.write_date,
                    "last_message_by": message.author_id.id,
                }
            )
        return message

    # -- Delete empty Conversations
    def _delete_conversations(self, conversation_ids):
        """
        Deletes all conversations with no messages left.
         Notifications are not considered!
        :param list conversation_ids: List of Conversation ids
        :return: just Return))
        """
        if len(conversation_ids) == 0:
            return
        # Delete empty Conversations
        conversations_2_delete = []

        for conversation in conversation_ids:
            message_count = self.search_count(
                [
                    ("res_id", "=", conversation),
                    ("model", "=", "cetmix.conversation"),
                    ("message_type", "in", ["email", "comment"]),
                ]
            )
            if message_count == 0:
                conversations_2_delete.append(conversation)

        # Delete conversations with no messages
        if len(conversations_2_delete) > 0:
            self.env["cetmix.conversation"].browse(conversations_2_delete).unlink()

    # -- Check delete rights
    def unlink_rights_check(self):
        """
        Check if user has access right to delete messages
        Raises Access Error or returns True
        :return: True
        """
        # Root
        if self.env.is_superuser():
            return True

        # Can delete messages?
        if not self.env.user.has_group("prt_mail_messages.group_delete"):
            raise AccessError(_("You cannot delete messages!"))

        # Can delete any message?
        if self.env.user.has_group("prt_mail_messages.group_delete_any"):
            return True

        # Check access rights
        partner_id = self.env.user.partner_id.id
        for rec in self:
            # Can delete if user:
            # - Is Message Author for 'comment' message
            # - Is the only 'recipient' for 'email' message

            # Sent
            if rec.message_type == "comment":

                # Is Author?
                if not rec.author_allowed_id.id == partner_id:
                    raise AccessError(
                        _(
                            "You cannot delete the following message"
                            "\n\n Subject: %s \n\n"
                            " Reason: %s"
                            % (rec.subject, _("You are not the message author"))
                        )
                    )

            # Received
            if rec.message_type == "email":

                # No recipients
                if not rec.partner_ids:
                    raise AccessError(
                        _(
                            "You cannot delete the following message"
                            "\n\n Subject: %s \n\n"
                            " Reason: %s"
                            % (rec.subject, _("Message recipients undefined"))
                        )
                    )

                # Has several recipients?
                if len(rec.partner_ids) > 1:
                    raise AccessError(
                        _(
                            "You cannot delete the following message"
                            "\n\n Subject: %s \n\n"
                            " Reason: %s"
                            % (rec.subject, _("Message has multiple recipients"))
                        )
                    )

                # Partner is not that one recipient
                if not rec.partner_ids[0].id == partner_id:
                    raise AccessError(
                        _(
                            "You cannot delete the following message"
                            "\n\n Subject: %s \n\n"
                            " Reason: %s"
                            % (rec.subject, _("You are not the message recipient"))
                        )
                    )

    # -- Unlink
    def unlink(self):

        # Avoid triggering for inheriting models
        if self._name != "mail.message":
            return super(MailMessage, self).unlink()

        # Store Conversation ids
        conversation_ids = []
        for rec in self.sudo():
            if rec.model == "cetmix.conversation":
                conversation_ids.append(rec.res_id)

        # Deleted from parent record?
        if self._context.get("force_delete", False):
            return super(MailMessage, self).unlink()

        # Delete messages linked with emails
        email_messages = self.filtered("is_mail_mail")
        len_email_messages = len(email_messages)
        if len_email_messages > 0:
            return super(MailMessage, email_messages).unlink()
        if len(self) == len_email_messages:
            return

        # Check access rights
        self.unlink_rights_check()

        # Unlink
        res = super(MailMessage, self).unlink()
        if len(conversation_ids) > 0:
            self._delete_conversations(conversation_ids)
        return res

    # -- Count ref Partners
    def _compute_ref_partner_count(self):
        for rec in self:
            rec.ref_partner_count = len(rec.ref_partner_ids)

    # Sometimes user has access to record but does not have access
    #  to author or recipients.
    # Below is a workaround for author, recipient and followers

    # -- Get allowed author
    @api.depends("author_id")
    def _compute_author_allowed(self):
        forbidden_partners = self.env["res.partner"]
        for rec in self:
            author_id = rec.author_id
            if author_id not in forbidden_partners:
                try:
                    author_id.check_access_rule("read")
                    rec.author_allowed_id = author_id
                except AccessError:
                    forbidden_partners += author_id

    # -- Get allowed recipients
    @api.depends("attachment_ids")
    def _compute_attachments_allowed(self):
        forbidden_records = []
        for rec in self:
            attachments_allowed = self.env["ir.attachment"]
            for attachment in rec.attachment_ids:
                att_obj = attachment.sudo().read(["res_model", "res_id"])[0]
                model = att_obj.get("res_model", False)
                res_id = att_obj.get("res_id", False)
                if (model, res_id) in forbidden_records:
                    continue
                try:
                    self.env[model].browse(res_id).check_access_rule("read")
                except AccessError:
                    forbidden_records += (model, res_id)
                    continue
                attachments_allowed += attachment

            rec.attachment_allowed_ids = attachments_allowed

    # -- Get allowed recipients
    @api.depends("partner_ids")
    def _compute_partners_allowed(self):
        forbidden_partners = self.env["res.partner"]
        for rec in self:
            recipients_allowed = self.env["res.partner"]
            for partner in rec.partner_ids - forbidden_partners:
                try:
                    partner.check_access_rule("read")
                    recipients_allowed += partner
                except AccessError:
                    forbidden_partners += partner

            rec.partner_allowed_ids = recipients_allowed

    # -- Search allowed authors
    @api.model
    def _search_author_allowed(self, operator, value):
        return [("author_id", operator, value)]

    # -- Get related record followers
    # Check if model has 'followers' field and user has access to followers

    @api.depends("record_ref")
    def _compute_message_followers(self):
        forbidden_partners = self.env["res.partner"]
        approved_models = []
        for rec in self:
            if rec.record_ref:

                # Check model
                model = rec.model
                if model not in approved_models:
                    if "message_partner_ids" in self.env[model]._fields:
                        approved_models.append(model)
                    else:
                        rec.ref_partner_ids = False
                        continue

                followers_allowed = self.env["res.partner"]
                for follower in rec.record_ref.message_partner_ids - forbidden_partners:
                    try:
                        follower.check_access_rule("read")
                        followers_allowed += follower
                    except AccessError:
                        forbidden_partners += follower
                rec.ref_partner_ids = followers_allowed
            else:
                rec.ref_partner_ids = False

    # -- Dummy
    def _compute_dummy(self):
        return

    # -- Get Subject for tree view
    @api.depends("subject")
    def _compute_subject_display(self):

        # Get config data
        ICPSudo = self.env["ir.config_parameter"].sudo()

        # Get preview length. Will use it for message body preview
        body_preview_length = int(
            ICPSudo.get_param(
                "cetmix.messages_easy_text_preview", DEFAULT_MESSAGE_PREVIEW_LENGTH
            )
        )
        # Get message subtype colors
        messages_easy_color_note = ICPSudo.get_param(
            "cetmix.messages_easy_color_note", default=False
        )
        mt_note = self.env.ref("mail.mt_note").id

        # Get current timezone
        tz = self.env.user.tz
        if tz:
            local_tz = pytz.timezone(tz)
        else:
            local_tz = pytz.utc

        # Get current time
        now = datetime.now(local_tz)
        # Compose subject
        for rec in self.with_context(bin_size=False):
            # Get message date with timezone
            message_date = pytz.utc.localize(rec.date).astimezone(local_tz)
            # Compose displayed date/time
            days_diff = (now.date() - message_date.date()).days
            if days_diff == 0:
                date_display = datetime.strftime(message_date, "%H:%M")
            elif days_diff == 1:
                date_display = " ".join(
                    (_("Yesterday"), datetime.strftime(message_date, "%H:%M"))
                )
            elif now.year == message_date.year:
                date_display = " ".join(
                    (str(message_date.day), _(MONTHS.get(message_date.month)))
                )
            else:
                date_display = str(message_date.date())

            # Compose notification icons
            notification_icons = ""
            if rec.needaction:
                notification_icons = '<i class="fa fa-envelope" title="%s"></i>' % _(
                    "New message"
                )
            if rec.starred:
                notification_icons = (
                    '%s &nbsp;<i class="fa fa-star" title="%s"></i>'
                    % (notification_icons, _("Starred"))
                )
            if rec.has_error > 0:
                notification_icons = (
                    '%s &nbsp;<i class="fa fa-exclamation" title="%s"></i>'
                    % (notification_icons, _("Sending Error"))
                )
            # .. edited
            if rec.cx_edit_uid:
                notification_icons = (
                    '%s &nbsp;<i class="fa fa-edit"'
                    ' style="color:#1D8348;"'
                    ' title="%s"></i>' % (notification_icons, rec.cx_edit_message)
                )
            # .. attachments
            if rec.attachment_count > 0:
                notification_icons = (
                    '%s &nbsp;<i class="fa fa-paperclip" title="%s"></i>'
                    % (
                        notification_icons,
                        "&#013;".join([a.name for a in rec.attachment_ids]),
                    )
                )

            # Compose preview body
            plain_body = html2plaintext(rec.body) if len(rec.body) > 10 else ""
            if len(plain_body) > body_preview_length:
                plain_body = "".join((plain_body[:body_preview_length], "..."))

            rec.subject_display = TREE_TEMPLATE % (
                ("background-color:%s;" % messages_easy_color_note)
                if messages_easy_color_note and rec.subtype_id.id == mt_note
                else "",
                _("Internal Note") if rec.subtype_id.id == mt_note else _("Message"),
                rec.author_avatar.decode("utf-8")
                if rec.author_avatar
                else IMAGE_PLACEHOLDER,
                rec.author_display,
                rec.author_display,
                rec.subject if rec.subject else "",
                str(message_date.replace(tzinfo=None)),
                date_display,
                "{}: {}".format(rec.model_name, rec.record_ref.display_name)
                if rec.record_ref
                else "",
                notification_icons,
                plain_body,
            )

    # -- Get Author for tree view
    @api.depends("author_allowed_id")
    def _compute_author_display(self):
        for rec in self:
            rec.author_display = (
                rec.author_allowed_id.name if rec.author_allowed_id else rec.email_from
            )

    # -- Count recipients
    @api.depends("partner_allowed_ids")
    def _compute_partner_count(self):
        for rec in self:
            rec.partner_count = len(rec.partner_allowed_ids)

    # -- Count attachments
    @api.depends("attachment_ids")
    def _compute_attachment_count(self):
        for rec in self:
            rec.attachment_count = len(rec.attachment_allowed_ids)

    # -- Count messages in same thread
    @api.depends("res_id")
    def _compute_thread_messages_count(self):
        for rec in self:
            rec.thread_messages_count = self.search_count(
                [
                    "&",
                    "&",
                    ("model", "=", rec.model),
                    ("res_id", "=", rec.res_id),
                    ("message_type", "in", ["email", "comment"]),
                ]
            )

    # -- Ref models
    @api.model
    def _referenceable_models(self):
        return [
            (x.model, x.name)
            for x in self.env["ir.model"].sudo().search([("transient", "=", False)])
        ]

    # -- Compose reference
    @api.depends("res_id")
    def _compute_record_ref(self):
        for rec in self:
            if rec.model and rec.res_id:
                res = self.env[rec.model].sudo().browse(rec.res_id)
                if res:
                    rec.record_ref = res
                else:
                    rec.record_ref = False
            else:
                rec.record_ref = False

    # -- Get forbidden models
    def _get_forbidden_models(self):

        # Use global vars
        global GHOSTS_CHECKED
        global FORBIDDEN_MODELS

        # Ghosts checked?
        if GHOSTS_CHECKED:
            return FORBIDDEN_MODELS[:]

        # Search for 'ghost' models. These are models left from uninstalled modules.
        self._cr.execute(
            """ SELECT model FROM ir_model
                                    WHERE transient = False
                                    AND NOT model = ANY(%s) """,
            (list(FORBIDDEN_MODELS),),
        )

        # Check each model
        for msg_model in self._cr.fetchall():
            model = msg_model[0]
            if not self.env["ir.model"].sudo().search([("model", "=", model)]).modules:
                FORBIDDEN_MODELS.append(model)

        # Mark as checked
        GHOSTS_CHECKED = True
        return FORBIDDEN_MODELS[:]

    # -- Open messages of the same thread
    def thread_messages(self):
        self.ensure_one()

        global TREE_VIEW_ID
        global FORM_VIEW_ID

        # Cache Tree View and Form View ids
        if not TREE_VIEW_ID:
            TREE_VIEW_ID = self.env.ref("prt_mail_messages.prt_mail_message_tree").id
            FORM_VIEW_ID = self.env.ref("prt_mail_messages.prt_mail_message_form").id

        return {
            "name": _("Messages"),
            "views": [[TREE_VIEW_ID, "tree"], [FORM_VIEW_ID, "form"]],
            "res_model": "mail.message",
            "type": "ir.actions.act_window",
            "target": "current",
            "domain": [
                ("message_type", "in", ["email", "comment"]),
                ("model", "=", self.model),
                ("res_id", "=", self.res_id),
            ],
        }

    # -- Return allowed message ids and forbidden model list
    @api.model
    def _find_allowed_doc_ids_plus(self, model_ids):
        IrModelAccess = self.env["ir.model.access"]
        allowed_ids = set()
        failed_models = []
        for doc_model, doc_dict in model_ids.items():
            if not IrModelAccess.check(doc_model, "read", False):
                failed_models.append(doc_model)
                continue
            allowed_ids |= self._find_allowed_model_wise(doc_model, doc_dict)
        return allowed_ids, failed_models

    # -- Search messages
    def _search_messages(self, args, limit=None, order=None):
        """
        This a shortcut function for mail.message model only
        """
        if expression.is_false(self, args):
            # optimization: no need to query, as no record satisfies the domain
            return []

        # the flush must be done before the _where_calc(),
        # as the latter can do some selects
        self._flush_search(args, order=order)

        query = self._where_calc(args)
        self._apply_ir_rules(query, "read")
        order_by = self._generate_order_by(order, query)
        from_clause, where_clause, where_clause_params = query.get_sql()

        where_str = where_clause and (" WHERE %s" % where_clause) or ""

        limit_str = limit and " limit %d" % limit or ""
        query_str = (
            'SELECT "mail_message".id,'
            ' "mail_message".model,'
            ' "mail_message".res_id FROM '
            + from_clause
            + where_str
            + order_by
            + limit_str
        )  # noqa E8103
        self._cr.execute(query_str, where_clause_params)
        res = self._cr.fetchall()
        return res

    # -- Override _search
    @api.model
    def _search(
        self,
        args,
        offset=0,
        limit=None,
        order=None,
        count=False,
        access_rights_uid=None,
    ):
        """ Mail.message overrides generic '_search' defined in 'model' to
         implement own logic for message access rights.
        However sometimes this does not work for us because
         we would like to show only messages posted to the records
        user actually has access to

        Following key in context is used:
        - 'check_messages_access': if not set legacy 'search' is performed

        For the moment we do not show messages posted to mail.channel
         Model (Discussion Channels)
        Finally we check the following:
        After having received ids of a classic search, keep only:
        - uid has access to related record
        - otherwise: remove the id
        """
        # Skip if not using our own _search
        if not self._context.get("check_messages_access", False):
            return super(MailMessage, self)._search(
                args=args,
                offset=offset,
                limit=limit,
                order=order,
                count=count,
                access_rights_uid=access_rights_uid,
            )
        # Rules do not apply to administrator
        if self.env.is_superuser():
            return super(MailMessage, self)._search(
                args,
                offset=offset,
                limit=limit,
                order=order,
                count=count,
                access_rights_uid=access_rights_uid,
            )
        # Non-employee see only messages with a subtype (aka, no internal logs)
        if not self.env.user.has_group("base.group_user"):
            args = [
                "&",
                "&",
                ("subtype_id", "!=", False),
                ("subtype_id.internal", "=", False),
            ] + list(args)

        # Get forbidden models
        forbidden_models = self._get_forbidden_models()

        # Remaining amount of records we need to fetch
        limit_remaining = limit

        # List of filtered ids we return
        id_list = []

        # id of the last message fetched
        # (in case we need to perform more fetches to fill the limit)
        last_id = False
        # Scrolling message list pages back (arrow left)
        scroll_back = False
        search_args = False
        # Fetch messages
        while limit_remaining if limit else True:

            # Check which records are we trying to fetch
            # Skip for count
            if not count:

                # For initial query only
                if not last_id:

                    # If fetching not the first page or performing search_count
                    if offset != 0:
                        last_offset = self._context["last_offset"]

                        # Scrolling back
                        if offset < last_offset:
                            scroll_back = True
                            search_args = ("id", ">", self._context["first_id"])
                            order = "id asc"

                        # Scrolling reverse from first to last page
                        elif last_offset == 0 and offset / limit > 1:
                            scroll_back = True
                            order = "id asc"

                        # Scrolling forward
                        elif offset > last_offset:
                            search_args = ("id", "<", self._context["last_id"])
                            order = "id desc"

                        # Returning from form view
                        else:
                            search_args = ("id", "<=", self._context["first_id"])
                            order = "id desc"
                    else:
                        search_args = False

                # Post fetching records
                else:
                    if scroll_back:
                        search_args = ("id", ">", last_id)
                        order = "id asc"
                    else:
                        search_args = ("id", "<", last_id)
                        order = "id desc"

            # Check for forbidden models and compose final args
            if search_args and len(forbidden_models) > 0:
                query_args = [
                    "&",
                    "&",
                    ("model", "not in", forbidden_models),
                    search_args,
                ] + list(args)
            elif search_args:
                query_args = ["&", search_args] + list(args)
            elif len(forbidden_models) > 0:
                query_args = ["&", ("model", "not in", forbidden_models)] + list(args)
            else:
                query_args = args

            # Get messages (id, model, res_id)
            res = self._search_messages(
                args=query_args, limit=limit_remaining if limit else limit, order=order
            )

            # All done, no more messages left
            if len(res) == 0:
                break

            # Check model access
            model_ids = {}
            for m_id, rmod, rid in res:
                if rmod and rid:
                    model_ids.setdefault(rmod, {}).setdefault(rid, set()).add(m_id)

            allowed_ids, failed_models = self._find_allowed_doc_ids_plus(model_ids)

            # Append to list of allowed ids,
            # re-construct a list based on ids,
            # because set did not keep the original order
            sorted_ids = [msg[0] for msg in res if msg[0] in allowed_ids]

            if len(sorted_ids) > 0:
                id_list += sorted_ids

            # Break if search was initially limitless
            if not limit:
                break

            # Add failed models to forbidden models
            if len(failed_models) > 0:
                forbidden_models += failed_models

            # Set last id
            last_id = res[-1][0]

            # Deduct remaining amount
            limit_remaining -= len(allowed_ids)

        if count:
            return len(id_list)
        else:
            return reversed(id_list) if scroll_back else id_list

    # -- Prepare context for reply or quote message
    def reply_prep_context(self):
        self.ensure_one()
        body = False
        wizard_mode = self._context.get("wizard_mode", False)

        if wizard_mode in ["quote", "forward"]:
            # Get current timezone
            tz = self.env.user.tz
            if tz:
                local_tz = pytz.timezone(tz)
            else:
                local_tz = pytz.utc
            # Get date and time format
            language = (
                self.env["res.lang"]
                .sudo()
                .search([("code", "=", self.env.user.lang)], limit=1)
            )
            # Compute tz-respecting date
            message_date = (
                pytz.utc.localize(self.date)
                .astimezone(local_tz)
                .strftime(" ".join([language.date_format, language.time_format]))
            )
            body = _(
                "<div font-style=normal;>"
                "<br/></div>"
                "<blockquote>----- Original message ----- <br/> Date: {} <br/>"
                " From: {} <br/> Subject: {} <br/><br/>{}</blockquote>".format(
                    message_date, self.author_display, self.subject, self.body
                )
            )

        ctx = {
            "default_res_id": self.res_id,
            "default_parent_id": False if wizard_mode == "forward" else self.id,
            "default_model": self.model,
            "default_partner_ids": [self.author_allowed_id.id]
            if self.author_allowed_id
            else [],
            "default_attachment_ids": self.attachment_ids.ids
            if wizard_mode == "forward"
            else [],
            "default_is_log": False,
            "default_body": body,
            "default_wizard_mode": wizard_mode,
        }
        return ctx

    # -- Reply or quote message
    def reply(self):
        self.ensure_one()
        # Mark as read
        self.mark_read_multi()

        return {
            "name": _("New message"),
            "views": [[False, "form"]],
            "res_model": "mail.compose.message",
            "type": "ir.actions.act_window",
            "target": "new",
            "context": self.reply_prep_context(),
        }

    # -- Move message
    def move(self):
        self.ensure_one()
        # Mark as read
        self.mark_read_multi()

        return {
            "name": _("Move messages"),
            "views": [[False, "form"]],
            "res_model": "prt.message.move.wiz",
            "type": "ir.actions.act_window",
            "target": "new",
        }

    # -- Assign author
    def assign_author(self):
        # Mark as read
        self.mark_read_multi()
        addr = parseaddr(self.email_from)
        return {
            "name": _("Assign Author"),
            "views": [[False, "form"]],
            "res_model": "cx.message.partner.assign.wiz",
            "type": "ir.actions.act_window",
            "target": "new",
            "context": {"default_name": addr[0], "default_email": addr[1]},
        }

    # -- Edit message
    def message_edit(self):
        # Mark as read
        self.mark_read_multi()
        self.ensure_one()
        return {
            "name": _("Edit"),
            "views": [[False, "form"]],
            "res_model": "cx.message.edit.wiz",
            "type": "ir.actions.act_window",
            "target": "new",
        }


################
# Res.Partner #
################
class Partner(models.Model):
    _inherit = "res.partner"

    messages_from_count = fields.Integer(
        string="Messages From", compute="_compute_messages_from_count"
    )
    messages_to_count = fields.Integer(
        string="Messages To", compute="_compute_messages_to_count"
    )

    # -- Count messages from
    @api.depends("message_ids")
    def _compute_messages_from_count(self):
        for rec in self:
            if rec.id:
                rec.messages_from_count = self.env["mail.message"].search_count(
                    [
                        ("author_id", "child_of", rec.id),
                        ("message_type", "in", ["email", "comment"]),
                        ("model", "!=", "mail.channel"),
                    ]
                )
            else:
                rec.messages_from_count = 0

    # -- Count messages from
    @api.depends("message_ids")
    def _compute_messages_to_count(self):
        for rec in self:
            rec.messages_to_count = self.env["mail.message"].search_count(
                [
                    ("partner_ids", "in", [rec.id]),
                    ("message_type", "in", ["email", "comment"]),
                    ("model", "!=", "mail.channel"),
                ]
            )

    # -- Open related
    def partner_messages(self):
        self.ensure_one()

        # Choose what messages to display
        open_mode = self._context.get("open_mode", "from")

        if open_mode == "from":
            domain = [
                ("message_type", "in", ["email", "comment"]),
                ("author_id", "child_of", self.id),
                ("model", "!=", "mail.channel"),
            ]
        elif open_mode == "to":
            domain = [
                ("message_type", "in", ["email", "comment"]),
                ("partner_ids", "in", [self.id]),
                ("model", "!=", "mail.channel"),
            ]
        else:
            domain = [
                ("message_type", "in", ["email", "comment"]),
                ("model", "!=", "mail.channel"),
                "|",
                ("partner_ids", "in", [self.id]),
                ("author_id", "child_of", self.id),
            ]

        # Cache Tree View and Form View ids
        global TREE_VIEW_ID
        global FORM_VIEW_ID

        if not TREE_VIEW_ID:
            TREE_VIEW_ID = self.env.ref("prt_mail_messages.prt_mail_message_tree").id
            FORM_VIEW_ID = self.env.ref("prt_mail_messages.prt_mail_message_form").id

        return {
            "name": _("Messages"),
            "views": [[TREE_VIEW_ID, "tree"], [FORM_VIEW_ID, "form"]],
            "res_model": "mail.message",
            "type": "ir.actions.act_window",
            "context": "{'check_messages_access': True}",
            "target": "current",
            "domain": domain,
        }

    # -- Send email from partner's form view
    def send_email(self):
        self.ensure_one()

        return {
            "name": _("New message"),
            "views": [[False, "form"]],
            "res_model": "mail.compose.message",
            "type": "ir.actions.act_window",
            "target": "new",
            "context": {
                "default_res_id": False,
                "default_parent_id": False,
                "default_model": False,
                "default_partner_ids": [self.id],
                "default_attachment_ids": False,
                "default_is_log": False,
                "default_body": False,
                "default_wizard_mode": "compose",
                "default_no_auto_thread": False,
            },
        }
