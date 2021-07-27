from odoo import fields, api, models, http, tools, _
from odoo.http import request, Response
from datetime import timedelta, date, datetime
import calendar, json
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from .main import mypager
PPG = 20
from odoo.addons.website.controllers.main import Website

 
class ExpenseSummary(http.Controller):


    @http.route('/expense_form', type='http', method="GET", auth='user', website=True, csrf=False)
    def render_expense_form(self, **kwargs):
        """
        Render Add Expense Form Template
        """
        categories = request.env['expense.category'].search([])
        accounts = request.env['bank.account'].search([])
        return request.render('budget_expense_management.expense_form_template',{'categories': categories,
                                                                             'accounts':accounts})

    @http.route('/my_expenses', type='json', auth="user", 
                website=True, methods=['DELETE'],  csrf=False) 
    def delete_expense(self, **kwargs):
        """
        Delete expense pointed by expense_id
        """
        data = json.loads(request.httprequest.data.decode('utf-8'))


        if 'expense_id' in data:
            expense_summary = request.env['expense.summary'] 
            record_to_delete = expense_summary.browse(data['expense_id']).unlink()

        return Response("success", status=200)

    @http.route('/my_expenses', type='json', auth="user", 
                website=True, methods=['PATCH'],  csrf=False) 
    def update_expense(self, **kwargs):
        """
        Delete expense pointed by expense_id
        """
        if request.env.user.has_group('budget_expense_management.budget_admin'):
            try:
                data = json.loads(request.httprequest.data.decode('utf-8'))
                exp_id = request.env['expense.summary'].browse([int(data['exp_id'])])
                if exp_id:
                    if data['date']:
                        date_obj = datetime.strptime(data['date'],'%m/%d/%Y').date()
                        exp_id.date = date_obj.strftime(DF)
                    if data['category']:
                        catg_obj = request.env['expense.category'].search([('name','=', data['category'])])
                        if catg_obj and catg_obj.name :
                            exp_id.exp_category_id = catg_obj.id
                    if data['description']:
                        exp_id.name = data['description']
                    if data['account']:
                        account_obj = request.env['bank.account'].search([('name','=', data['account'])])
                        if account_obj and account_obj.name :
                            exp_id.account_journal_id = account_obj.id
                    if data['location']:
                        exp_id.location = data['location']
                    if data['amount']:
                        newdata = data['amount'].replace('$','').replace(',', '')
                        exp_id.amount = float(newdata)
            except Exception as exc:
                print(exc)
                Response.status = "400"
                return "Error"
            Response.status = "200"
            return "success"
        else:
            Response.status = "400"
            return "fail"

    @http.route('/my_expenses', type='http', auth="user", 
                website=True, methods=['POST'],  csrf=False)
    def add_expense(self, **post):
        """
        Add new expense
        """
        expense_summary = request.env['expense.summary']
        expense_id = expense_summary.create({
                    'name':post.get('name', False),
                    'date':post.get('date', False),
                    'exp_category_id':post.get('category', False),
                    'account_journal_id':post.get('account', False),
                    'amount':post.get('expense_amount', False),
                    'location':post.get('location', False),
                    'user_id': request.env.user.id or False
        })
        return Response("success", status=200)

    @http.route([
        '/my_expenses',
        '/my_expenses/page/<int:page>',
    ], type='http', auth="user", methods=['GET'], website=True, csrf=False)
    def show_expense(self, page=0, ppg=False,  **post):
        """
        Return all expenses
        """
        if ppg:
            try:
                ppg = int(ppg)
            except ValueError:
                ppg = PPG
            post["ppg"] = ppg
        else:
            ppg = PPG
        expense_summary = request.env['expense.summary']
        domain = [('date','<=',fields.Date.today())]
        expenses = expense_summary.sudo().search(domain, order=post.get('order'))
        exp_catg_ids = request.env['expense.category'].search([]).mapped('name')
        account_id_list = request.env['bank.account'].search([]).mapped('name')

        pager = mypager(self, url='/my_expenses', total=len(expenses), page=page, step=ppg)
        offset = pager['offset']
        expenses = expenses[offset: offset + ppg]
        values = {
                    'my_expenses': expenses,
                    'catg_ids' : exp_catg_ids,
                    'accounts' :account_id_list,
                    'pager':pager,
                 }
        return request.render("budget_expense_management.portal_my_expenses", values)
