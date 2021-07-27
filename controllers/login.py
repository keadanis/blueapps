from odoo.addons.website.controllers.main import Website
from odoo import http
from odoo.http import request

class BudgetWebsite(Website):

    # ------------------------------------------------------
    # Login - overwrite of the web login so that regular users are redirected to the backend
    # while portal users are redirected to the frontend by default
    # ------------------------------------------------------

    @http.route(website=True, auth="public")
    def web_login(self, redirect=None, *args, **kw):
        response = super(BudgetWebsite, self).web_login(redirect=redirect, *args, **kw)

        is_valid_session = request.session.uid != None
        if not redirect and request.params['login_success'] or is_valid_session:
            uid = request.env['res.users'].browse(request.uid)
            is_valid_user = uid.has_group('budget_expense_management.budget_admin') or \
                            uid.has_group('budget_expense_management.budget_user')
            if is_valid_user:
                redirect = '/budget_monthly_rpt/'
            else:
                redirect = '/my'
            return http.redirect_with_hash(redirect)
        return response

    @http.route('/', type='http', auth="public", website=True)
    def index(self, **kw):
        return request.redirect('/web/login')
