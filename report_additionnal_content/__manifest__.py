# Copyright Sudokeys (www.sudokeys.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Report Additionnal Content",
    "summary": """
        SUDOKEYS has put at your disposal an app allowing you to add content to all your reports whatever they are: quote, purchase order, invoice, delivery order, …
    """,
    "version": "14.0.1.0.1",
    "development_status": "Production/Stable",
    "category": "Technical",
    "images": ["static/description/banner.png"],
    "website": "https://github.com/OCA/None",
    "author": "Sudokeys, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "base",
    ],
    "data": [
        # Security
        "security/ir.model.access.csv",
        # Views
        "views/ir_actions_report_view.xml",
    ],
}
