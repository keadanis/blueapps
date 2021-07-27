import json
import logging

import requests
from odoo import http

_logger = logging.getLogger(__name__)



class Custom_calendar_controller(http.Controller):
    @http.route('/get_auth_code', type="http", auth="public", website=True)
    def get_auth_code(self, **kwarg):
        client_details = http.request.env['res.users'].sudo().search([], limit=1).company_id

        if kwarg.get('code'):
            '''To Get access Token and store'''

            client_details.write({'authorization_url': kwarg.get('code')})
            if client_details:
                application_id = client_details.application_id
                client_secret = client_details.client_secret
                redirect_uri = client_details.redirect_uri
                request_token_url = 'https://login.microsoftonline.com/common/oauth2/v2.0/token?scope=onlinemeetings.readwrite'
                headers = {"Content-type": "application/x-www-form-urlencoded"}
                data = {
                    'client_id': application_id,
                    'code': kwarg.get('code'),
                    'redirect_uri': redirect_uri,
                    'grant_type': "authorization_code",
                    'client_secret': client_secret
                }

                response = requests.post(request_token_url, data=data, headers=headers)

                print(response.status_code)
                print(kwarg.get('code'))
                print(application_id)
                print(client_secret)
                if response.status_code == 200:
                    parsed_token_response = json.loads(response.text.encode('utf8'))
                    client_details.write({"access_token": parsed_token_response.get('access_token'),
                                    "refresh_token": parsed_token_response.get('refresh_token')})
                    url = "https://graph.microsoft.com/v1.0/me"
                    bearer = 'Bearer ' + parsed_token_response.get('access_token')
                    headers = {
                        'Content-Type': "application/json",
                        'Authorization': bearer
                    }

                    requests_response = requests.request("GET", url, headers=headers)
                    if requests_response.status_code == 200:
                        parsed_response = requests_response.json()
                        print(parsed_response.get('displayName'))

        return "You Can Close this window"
