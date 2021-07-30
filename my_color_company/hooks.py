from odoo import SUPERUSER_ID, api

from .models.res_company import URL_BASE


def uninstall_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env["ir.attachment"].search([("url", "=like", "%s%%" % URL_BASE)]).unlink()


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env["res.company"].search([]).scss_create_or_update_attachment()
    env["res.company"].search([]).color_defults()
