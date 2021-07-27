# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Reporte excel',
    'version': '1.0',
    'category': 'Sale',
     'description': '''
        Reporte excel.
    ''',
    'website': 'http://www.trescloud.com',
    'author': 'TRESCLOUD CIA LTDA',
    'maintainer': 'TRESCLOUD CIA. LTDA.',
    'license': 'OPL-1',
    'depends': ['base'],
    'data': [
        'views/base_file_report.xml'
    ],
    'installable': True,
    'application': False,
    "price": 0,
    "currency": "USD",
    'images': [
        'static/description/icon.png',
        'static/description/logo_trescloud.png'
    ],
}
