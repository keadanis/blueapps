# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
from werkzeug.exceptions import Forbidden, NotFound
from odoo.addons.website.controllers.main import QueryURL

from odoo import http
from odoo.http import request

class ARTheme(http.Controller):
    
    @http.route('/welcome/', auth='public')
    def  index(self, **kw):
        return "Welcome!"