# Copyright 2020 Manish Kumar Bohra <manishbohra1994@gmail.com> or <manishkumarbohra@outlook.com>
# License LGPL-3 - See http://www.gnu.org/licenses/Lgpl-3.0.html

{
    'name': 'CRM Refresh',
    'version': '14.0',
    'summary': 'This module allows user to reload the CRM screen without refresh the webpage',
    'description': 'This module allows user to reload the CRM screen without refresh the webpage',
    'category': 'CRM',
    'author': 'Manish Bohra',
    'website': 'www.linkedin.com/in/manishkumarbohra',
    'maintainer': 'Manish Bohra',
    'support': 'manishkumarbohra@outlook.com',
    'sequence': '10',
    'license': 'LGPL-3',
    "data": [
        'views/crm_refresh.xml',
    ],
    'images': ['static/description/reload.gif'],
    'depends': ['crm'],
    'installable': True,
    'auto_install': False,
    'application': True,
}
