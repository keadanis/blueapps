# -*- coding: utf-8 -*-
##############################################################################
#
#    ODOO Open Source Management Solution
#
#    ODOO Addon module by Sprintit Ltd
#    Copyright (C) 2020 Sprintit Ltd (<http://sprintit.fi>).
#
##############################################################################


{
    'name': 'Sprintit Work Order Sorting',
    'version': '14.0.1.0.0',
    'license': 'LGPL-3',
    'category': 'Manufacturing/Manufacturing',
    'description': 'MRP production Work Order Sorting based on Deadline Start Date',
    'author': 'Sprintit ltd',
    'maintainer': 'SprintIT',
    'website': 'https://sprintit.fi/in-english',
    'depends': [ 
        'mrp',
    ],
    'data': [
        'view/assets.xml',
        'view/mrp_view.xml',
        
    ],
    'demo': [
    ],
    'test': [
    ],
    'images': ['static/description/cover.jpg',],
    "external_dependencies": {},
    'installable': True,
    'auto_install': False,
    'price': 0.0,
    'currency': 'EUR',
 }

