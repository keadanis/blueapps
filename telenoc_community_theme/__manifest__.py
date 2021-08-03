{
    "name": "Telenoc Community Theme",
    "summary": "Odoo Community Backend Theme",
    "version": "14.0.1.0.0",
    "category": "Themes/Backend",
    "website": "http://www.telenoc.org/",
    "author": "Odoo Team, Telenoc",
    "license": "LGPL-3",
    "installable": True,
    "depends": ["web", "mail"],
    

    "data": ["views/assets.xml", "views/res_users.xml", "views/web.xml"],
    "qweb": [
        "static/src/xml/apps.xml",
        "static/src/xml/form_buttons.xml",
        "static/src/xml/menu.xml",
        "static/src/xml/navbar.xml",
        "static/src/xml/attachment_viewer.xml",
        "static/src/xml/discuss.xml",
        "static/src/xml/control_panel.xml",
        "static/src/xml/search_panel.xml",
    ],
        'images': ['static/description/banner.png',
              'static/description/theme_screenshot.png'],
    "sequence": 1,
}
