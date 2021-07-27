# -*- encoding: utf-8 -*-
#
# Module written to Odoo, Open Source Management Solution
#
# Copyright (c) 2021 Wedoo - https://wedoo.tech/
# All Rights Reserved.
#
# Developer(s): Alan Guzmán
#               (age@wedoo.tech)
########################################################################
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
########################################################################

{
    'name': 'Wedoo | Split lead',
    'author': 'Wedoo ©',
    'category': 'CRM',
    'sequence': 50,
    'summary': "Split lead percentages worked by commercial",
    'website': 'https://www.wedoo.tech/',
    'version': '1.0',
    'license': 'AGPL-3',
    'description': """
Split lead
=================
This module adds a new tab to register the users who participated in it and
who obtained the percentages, in addition the percentage of the lines was
equal to the percentage of the opportunity.
    """,
    'depends': [
        'base',
        'crm',
        'sale_crm',
        'sale'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/split_lead_view.xml',
        'views/split_lead_pivot_view.xml',
        'views/inherit_crm_lead_view.xml'
    ],
    'images': [
        'static/description/split_description.png',
        'static/description/split_screenshot.png',
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': False,
}
