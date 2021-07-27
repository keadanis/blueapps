# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta
from datetime import datetime, date, timedelta as td
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.osv import expression
from dateutil.relativedelta import relativedelta
import re
import time
import math
import string
import dateutil.parser
import werkzeug.urls
import logging

_logger = logging.getLogger(__name__)


class MenusHide(models.TransientModel):
    _name = "menus.hide"
    
    
    groups = fields.Many2many('res.groups','menu_hide_groups_rel','menu_id','group_id','Groups')
    menus_hide_ids = fields.Many2many('ir.ui.menu','menu_hide_groups_menu_rel','menu_hide_id','menu_id','Menus') 
    
    
    
    @api.multi
    def groups_assign_to_menus(self):
        self.menus_hide_ids.sudo().write({'groups_id':[(6,0,self.groups.ids)]})
        
    
