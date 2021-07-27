##############################################################################
#
#    Copyright (c) 2020 Er. Vaidehi Vasani
#    All Right Reserved
#
#    See LICENSE file for full licensing details.
##############################################################################
{
    'name': 'Contract Creator',
    'author': 'Er. Vaidehi Vasani',
    'version': '14.0.1.0.0',
    'category': 'Sales',
    'license': 'OPL-1',
    'author': 'Er. Vaidehi Vasani',
    'maintainer': 'Er. Vaidehi Vasani',
    'depends': [
        'sale',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/contract_creator.xml',
        'views/contract_template.xml',
        'report/contract_report.xml',
    ],
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'price': 0.00,
    'currency': 'EUR',
}
