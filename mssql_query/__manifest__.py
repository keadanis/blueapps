{

     'name': "MS SQL Query",
     'author': "Fasil",
     'version': '0.1',
     'sequence': -1,
     'website': '',
    'license': 'LGPL-3',
     'summary': """
             The app for making easy queries in MS SQL""",
     'description': """
Explore your MS SQL database with query into an Odoo interface
You can use SELECT, UPDATE, DELETE, CREATE, INSERT, ALTER and DROP statements.

         """,
     'depends': ['base'],
     'data': [
         'security/ir.model.access.csv',
         'security/security.xml',
         'views/mssql_query.xml',
     ],
    'demo': [],

    'installable': True,
    'application': True,
    'auto_install': False,
     'images': ['static/description/banner.gif'],

}
