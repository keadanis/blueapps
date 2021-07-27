import json
import logging
import requests
from odoo import http
from odoo import api, fields, models
from odoo.exceptions import Warning, UserError

_logger = logging.getLogger(__name__)


class CustomMeet(models.Model):
    _inherit = 'calendar.event'
    _description = 'Team Meet Details'

    team_flag = fields.Boolean('Add Team Meet', default=False)
    end_date_time = fields.Datetime(string='End Date', index=True)
    team_url = fields.Text(string='Meet URL')
    team_id = fields.Text(string='Meet ID')

    def action_id_calendar_view(self):
        calendar_view = self.env.ref('calendar.view_calendar_event_calendar')
        action_id = self.env['ir.actions.act_window'].search([('view_id', '=', calendar_view.id)], limit=1).id
        return action_id

    def base_url(self):
        url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return url

    def db_name(self):
        db_name = self._cr.dbname
        return db_name


    def create_attendees(self):
        current_user = self.env.user
        result = {}
        for meeting in self:
            alreay_meeting_partners = meeting.attendee_ids.mapped('partner_id')
            meeting_attendees = self.env['calendar.attendee']
            meeting_partners = self.env['res.partner']
            for partner in meeting.partner_ids.filtered(lambda partner: partner not in alreay_meeting_partners):
                values = {
                    'partner_id': partner.id,
                    'email': partner.email,
                    'event_id': meeting.id,
                }

                if self._context.get('google_internal_event_id', False):
                    values['google_internal_event_id'] = self._context.get('google_internal_event_id')

                # current user don't have to accept his own meeting
                if partner == self.env.user.partner_id:
                    values['state'] = 'accepted'

                attendee = self.env['calendar.attendee'].create(values)

                meeting_attendees |= attendee
                meeting_partners |= partner

            # # # if meeting_attendees and not self._context.get('detaching'):
            # # #     to_notify = meeting_attendees.filtered(lambda a: a.email != current_user.email)
            # # #     to_notify._send_mail_to_attendees('calendar.calendar_template_meeting_invitation')

            if meeting_attendees:
                meeting.write({'attendee_ids': [(4, meeting_attendee.id) for meeting_attendee in meeting_attendees]})

            if meeting_partners:
                meeting.message_subscribe(partner_ids=meeting_partners.ids)

            # We remove old attendees who are not in partner_ids now.
            all_partners = meeting.partner_ids
            all_partner_attendees = meeting.attendee_ids.mapped('partner_id')
            old_attendees = meeting.attendee_ids
            partners_to_remove = all_partner_attendees + meeting_partners - all_partners

            attendees_to_remove = self.env["calendar.attendee"]
            if partners_to_remove:
                attendees_to_remove = self.env["calendar.attendee"].search([('partner_id', 'in', partners_to_remove.ids), ('event_id', '=', meeting.id)])
                attendees_to_remove.unlink()

            result[meeting.id] = {
                'new_attendees': meeting_attendees,
                'old_attendees': old_attendees,
                'removed_attendees': attendees_to_remove,
                'removed_partners': partners_to_remove
            }
        return result


    def send_mail_notification_mail(self):
        client_details = http.request.env['res.users'].sudo().search([], limit=1).company_id
        login_user_id = self.env['res.users'].sudo().search([('id', '=', self._context.get('uid'))], limit=1)
        for i in self.attendee_ids:
            print(i.email)
            if i.partner_id != login_user_id.partner_id:
                if client_details.access_token and client_details.refresh_token:
                    bearer = 'Bearer ' + client_details.access_token
                    payload = {}
                    head = {
                        'Content-Type': "application/json",
                        'Authorization': bearer,
                        'Accept-Language': "en"
                    }
                    body = {
                        "message": {
                            "subject": self.name,
                            "body": {
                                "contentType": "HTML",
                                "content": "<div><a>You Are Invited to Meeting</a>""<p>"+self.name+"</p>""</div><dev><ul><li>Meeting URL: <a target=""_blank"" href="+self.team_url+">Join a Team Meeting</a></li><li>Meeting Date: <a>"+fields.Datetime.context_timestamp(self, self.start).isoformat(' ')+"</a></li><li>Meeting Description: <a>"+self.description+"</a></li> </ul></div>"                                    },
                            "toRecipients": [
                                {
                                    "emailAddress": {
                                    "address": i.email,
                                        }
                                }
                                            ],
                            "ccRecipients": [
                                {
                                    "emailAddress": {
                                    "address": "danas@contoso.onmicrosoft.com"
                                        }
                                }
                                            ]
                                },
                            "saveToSentItems": "false"
                            }
                    data_json = json.dumps(body)
                    url = 'https://graph.microsoft.com/v1.0/me/sendMail'
                    response = requests.post(url, data=data_json, headers=head)
        return True



    @api.model
    def create(self, vals_list):
        res = super(CustomMeet, self).create(vals_list)
        if vals_list.get('team_flag'):
            res.post_request_team_meet()
            res.send_mail_notification_mail()
        return res

    def redirect_team_meet(self):
        url = self.team_url
        return {
            "type": "ir.actions.act_url",
            "url": url,
            "target" : "new"
           }

    def post_request_team_meet(self):
        client_details = http.request.env['res.users'].sudo().search([], limit=1).company_id
        client_details.generate_refresh_token_from_access_token()

        start = fields.Datetime.context_timestamp(self, self.start).isoformat('T')
        end_datetime = fields.Datetime.context_timestamp(self, self.end_date_time).isoformat('T')
        if client_details.access_token and client_details.refresh_token:
            bearer = 'Bearer ' + client_details.access_token
            payload = {}
            head = {
                'Content-Type': "application/json",
                'Authorization': bearer,
                'Accept-Language': "en"
            }

            body = {
                "startDateTime": start,
                "endDateTime": end_datetime,
                "subject": self.name
            }
            data_json = json.dumps(body)
            url = 'https://graph.microsoft.com/v1.0/me/onlineMeetings'
            response = requests.post(url, data=data_json, headers=head)
            if response.status_code == 201:
                data_rec = response.json()
                self.write({"team_url": data_rec.get('joinWebUrl'), "team_id": data_rec.get('id')})
            elif response.status_code == 401:
                raise UserError("Please Authenticate with Microsoft Team.")
