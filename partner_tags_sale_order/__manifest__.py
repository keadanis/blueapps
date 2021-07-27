# Copyright 2020 Holoborodko Bohdan
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Partner Tags in Sale Order",
    "summary": "Show partner tags in sale order",
    "version": "12.0.1.0.0",
    "category": "Tools",
    "website": "https://holoborodko.com.ua/?ref=partner_tags_sale_order",
    "author": "Bohdan Holoborodko",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "contacts",
        "sale",
    ],
    "data": [
        "views/sale_order.xml",
        "views/res_partner.xml",
    ],
    'images': [
        'static/description/baner.png',
        'static/description/partner-sales-tag.png',
    ],
}
