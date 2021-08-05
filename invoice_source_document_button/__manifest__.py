# -*- coding: utf-8 -*-
{
    'name': "SW - Invoice Source Document Button",
    'summary': """
         Easily track the source documents for all your Invoices and Vendor Bills.
         """,
    'description': """
        A smart button to directly link all of your Invoices and Vendor bills with their related Purhase Orders & Sale Orders and access them. 
    """,
    'license':  "Other proprietary",
    'author': "Smart Way Business Solutions",
    'website': "https://www.smartway.co",
    'category': 'Accounting',
    'version': '1.0',
    'depends': ['base','account','purchase','sale'],
    'data': [
        'views/account_invoice_views.xml',
    ],
    "images":  ['static/description/Image.png'],
}
