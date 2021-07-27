# -*- coding: utf-8 -*-
##########################################################################
# Author      : Nevioo Technologies (<https://nevioo.com/>)
# Copyright(c): 2020-Present Nevioo Technologies
# All Rights Reserved.
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
# You should have received a copy of the License along with this program.
##########################################################################
{
    "name":  "Document Storage Location",
    "summary":  "This module allows you to store documemts at any location.",
    "category":  "Document",
    "version":  "14.0.1.1",
    "sequence":  1,
    "author":  "Nevioo Technologies",
    "website":  "www.nevioo.com",
    "license": 'OPL-1',
    "images": ['static/description/Banner.png'],
    "depends":  ['base','hr'],
    'data': [
                'security/ir.model.access.csv',
                'views/document_view.xml',
                'views/res_partner_view.xml',
                'views/hr_employee_view.xml',
                'views/menu.xml',
            ],
    "application":  True,
    "installable":  True,
    "auto_install":  False,
}
