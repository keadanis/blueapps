##############################################################################
#    Copyright (C) 2018 maachmedia. All Rights Reserved
{
    'name': 'Odoo Dynamic Export',
    'version': '1.0',
    'author': "Maach Softwares/ Maduka Sopulu",
    'category': 'Export/ Reports',
    'summary': 'Odoo Dynamic report to Excel for Odoo',

    'description': "This module enables users to print different types of model records in excel",
    "website": "https://maachmedia.ng",
    "data": [
        'wizard/odoo_dynamic_report_view.xml',
        'security/ir.model.access.csv',
    ],
    "images": ['images/export_img.png'],
    "application": True, 

}
