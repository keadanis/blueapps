{
    'name': 'Google Contacts helper',
    'author': 'Kareem Abuzaid, kareem.abuzaid123@gmail.com',
    'website': 'https://kareemabuzaid.com',
    'version': '13.0.1.0',
    'category': 'Tools',
    'summery': 'Add Google Contacts to settings page',
    'description': """
        Add Google contacts to settings page
    """,
    'data': [
        'views/res_config_settings_views.xml'
    ],
    'depends': [
        'base',
        'base_setup',
    ],
    'installable': True,
    'auto_install': True,
    'application': False,
}