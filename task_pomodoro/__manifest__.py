# -*- coding: utf-8 -*-
{
    'name': "Pomodoro for Task",

    'summary': """
        Add pomodoro timer to a task.
        """,

    'description': """
        Pomodoro is a concept of having small breaks between focus periods.
        That is to improve productivity. This module adds timer to a task,
        tracks number of pomodoros.

        https://en.wikipedia.org/wiki/Pomodoro_Technique
    """,

    'author': "Moc Diep",
    'website': "https://mocdiep.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'project',
    'version': '0.4',
    'price': 0.0,
    'currency': 'EUR',
    'licence': 'GPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base', 'project'],

    'images': ['static/description/banner.png'],

    # always loaded
    'data': [
        'views/assets.xml',
        'views/pmdr_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
