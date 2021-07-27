# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################
{
    'name': 'Float Speedometer',
    'version': '1.0',
    'category': 'All',
    'summary': "Float speedometer helps you to add speedometer widget in float field.",
    'description': "Float speedometer helps you to add speedometer widget in float field.",
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'website': 'http://www.acespritech.com',
    "depends": ['web','base','sale','fleet'],
    'currency': 'EUR',
    'price': 0.0,
    "data": [
        'views/templates.xml',
        'partner/partner_view.xml'
    ],
    'qweb': [
        "static/src/xml/widget.xml"
    ],
    'images': ['static/description/float_speedometer.png'],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

