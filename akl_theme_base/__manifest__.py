# -*- coding: utf-8 -*-
{
    'name': "akl_theme_base",

    'summary': """
        akl theme base, theme for everyone""",

    'description': """
        akl theme base, backend theme for everyone
    """,

    'author': "funenc odoo team",
    'website': "http://www.funenc.com",
    'live_test_url': "http://theme.aklbase.funenc.com",

    "category": "Themes/Backend",
    'version': '14.0.0.4',
    'license': 'OPL-1',
    'images': ['static/description/banner.png',
               'static/description/akl_screenshot.png'],

    'depends': ['base'],
    
    "application": False,
    "installable": True,
    "auto_install": False,

    'data': [
        'security/ir.model.access.csv',
        'views/akl_assets.xml',
        'views/akl_login.xml',
        'views/akl_base.xml',
    ],

    'qweb': [
        'static/xml/*.*',
    ]
}
