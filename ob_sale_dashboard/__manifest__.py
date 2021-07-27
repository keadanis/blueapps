{
    'name': "Sale Dashboard",

    'summary': """
            Sale Dashboard.""",

    'description': """ Sales Dashboard View """,

    'author': "Odoo Being, Odoo SA",
    'website': "https://www.odoobeing.com",
    'license': 'AGPL-3',
    'category': 'Sales',
    'version': '14.0.1.0.1',
    'support': 'odoobeing@gmail.com',
    'images': ['static/description/images/ob_sale_dashboard.png'],
    'installable': True,
    'auto_install': False,
    "depends": ['sale_management'],
    "data": [
        'views/sale_dashboard_assets.xml',
        'views/sale_order.xml',
    ],
    'qweb': [
        'static/src/xml/sale_dashboard.xml',
    ],
}
