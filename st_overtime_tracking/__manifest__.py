# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Overtime Tracking',
    'version': '1.0',
    'summary': 'Overtime',
    'sequence': 15,
    'description': """
    """,
    'category': 'Human Resources/Time Off',
    'author': 'Maik Steinfeld',
    'website': "https://www.steinfeld.one",
    'images': [],
    'depends': [
        'hr_timesheet',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_track_views.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license':'LGPL-3',
    'images':[
        'images/module_image.png',
        ],
    'price': 0.00,
    'currency':'EUR',
}
