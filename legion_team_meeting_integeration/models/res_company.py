# -*- coding: utf-8 -*-
import json
import logging
from datetime import datetime
import requests
import base64
from dateutil.parser import parse as duparse
from odoo import api, fields, models
from odoo.exceptions import Warning

_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = "res.company"

    application_id = fields.Char("Application Id",help="The application ID you obtain from the microsoft team app.")
    client_secret = fields.Char("Client Secret",help="The client Secret key you obtain from the microsoft team.")
    authorization_url = fields.Char("Authorization URL",help="")
    redirect_uri = fields.Char("Redirect URIs",help="",default="http://localhost:8069/get_auth_code")
    auth_code = fields.Char("Auth Code",help="")
    access_token = fields.Char("Access Token",help="")
    refresh_token = fields.Char("Refresh Token",help="")

    def users_authentic(self):
        team_auth_endpt = 'https://login.microsoftonline.com/common/oauth2/v2.0/authorize?'
        access_type = 'offline'
        client_id = self.application_id
        redirect_uri = self.redirect_uri

        url = team_auth_endpt + 'client_id='+ client_id +'&response_type=code&redirect_uri=' + redirect_uri + '&response_mode=query&scope=offline_access%20user.read%20mail.send%20onlinemeetings.readwrite&state=12345'


        return {
            "type": "ir.actions.act_url",
            "url": url,
            "target": "new"
        }

    def generate_refresh_token_from_access_token(self):
        client_id = self.application_id
        client_secret = self.client_secret
        redirect_uri = self.redirect_uri
        refresh_token = self.refresh_token
        request_token_url = 'https://login.microsoftonline.com/common/oauth2/v2.0/token?scope=offline_access%20user.read%20onlinemeetings.readwrite'
        headers = {"Content-type": "application/x-www-form-urlencoded"}
        data = {
            'client_id': client_id,
            'refresh_token': refresh_token,
            'redirect_uri': redirect_uri,
            'grant_type': "refresh_token",
            'client_secret': client_secret
        }

        response = requests.post(request_token_url, data=data, headers=headers)

        if response.status_code == 200:
            parsed_response = response.json()
            self.access_token = parsed_response.get('access_token')
        elif response.status_code == 401:
            _logger.error("Access token/refresh token is expired")
        else:
            raise Warning("We got a issue !!!! Desc : {}".format(response.text))
