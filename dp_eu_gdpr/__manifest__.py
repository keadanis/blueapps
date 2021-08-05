# Copyright 2018-Today datenpol gmbh (<https://www.datenpol.at/>)
# License OPL-1 or later (https://www.odoo.com/documentation/user/13.0/legal/licenses/licenses.html#licenses).

# noinspection PyStatementEffect
{
    'name': """DP EU-GDPR""",
    'summary': """General Data Protection Regulation""",
    'description': """DSGVO, EU-DSGVO, GDPR, EU-GDPR, General Data Protection Regulation, Dateschutzgrundverordnung, Datenschutz-Grundverordnung, RGPD, Règlement général sur la protection des données, Right of Access, Right to rectification, Right to erasure, Right to restriction of processing, Right to data portability, Right to object""",
    'category': 'Extra Tools',
    'version': '14.0.1.0.0',
    'license': 'OPL-1',
    'author': 'datenpol gmbh',
    'support': 'office@datenpol.at',
    'website': 'https://www.datenpol.at/',
    'depends': [
        'base',
        'mail_bot',
    ],
    'data': [
        'data/sequence.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/eu_gdpr_log_views.xml',
        'views/assets.xml',
        'wizards/eu_gdpr.xml',
    ],
    'images': ['static/description/Banner.jpg'],
    'installable': True,
    'auto_install': False,
    'application': True,
}
