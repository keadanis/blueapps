# -*- coding: utf-8 -*-
#
#############################################################################
#
#    Copyright (C) 2021-Antti Kärki.
#    Author: Antti Kärki.
#    email: antti.rocker.karki@outlook.com

#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################


{
    'name': 'Rocker Timesheet',
    'summary': 'hr_timesheet supercharged',
    'description': 'Probably most fastes way to report work done',
    'author': 'Antti Kärki',
    'license': 'AGPL-3',
    'version': '14.0.1.0',
    'category': 'Generic Modules/Human Resources',
    'sequence': 23,
    'website': '',
    'depends': ['base', 'project', 'hr_timesheet'],
    'data': [
        'security/rocker_timesheet_security.xml',
        'security/ir.model.access.csv',
        'views/rocker_template.xml',
        'views/rocker_timesheet_views.xml',
        'views/rocker_timesheet_about.xml',
        # 'data/rocker_timesheet_data.xml',
    ],
    # 'demo': [
    #     # 'data/rocker_timesheet_demo.xml',
    # ],
    'qweb': ['static/src/xml/rocker_button.xml'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'images': ['static/description/main_screenshot.gif'],

}
