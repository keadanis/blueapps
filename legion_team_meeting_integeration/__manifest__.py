{
    'name': 'Odoo Microsoft Team Meeting Integration',
    'version': '14.0.1.0.0',
    'author': 'Bytelegion',
    'website': 'https://www.bytelegions.com',
    'depends': ['calendar'],
    'license': 'AGPL-3',
    'category': 'Meetings',
    'company': 'Bytelegion',
    'summary': 'Join Microsoft Team Meetings',
    'description': '''
A Module To Join Team  Meeting in Odoo easily
''',
    'data': [
        'views/res_company_view.xml',
        'views/meeting.xml',
    ],
    'currency': 'USD',
    'price': 0,
    'installable': True,
    'application': True,
    'auto_install': False,
    'images': ['static/description/icon.png','static/description/main_screenshot.png']
}
