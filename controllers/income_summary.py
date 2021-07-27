from odoo import fields, api, models, http, tools, _
from odoo.http import request, Response
from datetime import timedelta, date, datetime
import json
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from .main import mypager
PPG = 20

class IncomeSummary(http.Controller):

    @http.route('/income_form/', type='http', method="GET", auth='user', website=True, csrf=False)
    def render_income_form(self, **kwargs):
        categories = request.env['income.category'].search([])
        accounts = request.env['bank.account'].search([])
        return request.render('budget_expense_management.inc_summ_template',{'categories': categories,
                                                                             'accounts':accounts})

    @http.route('/my_incomes', type='http', auth="user", website=True, methods=['POST'],  csrf=False)
    def add_income(self, **post):
        """
        Add new income
        """
        income_summary = request.env['income.summary']
        income_id = income_summary.create({
                    'name':post.get('name', False),
                    'date':post.get('date', False),
                    'income_categ_id':post.get('category', False),
                    'account_journal_id':post.get('account', False),
                    'amount':post.get('income_amount', False),
                    'user_id':request.env.user.id
        })
        return Response("success", status=200)

    @http.route(['/my_incomes','/my_incomes/page/<int:page>'], type='http', auth="user", website=True, methods=['GET'],  csrf=False)
    def show_incomes(self, page=0, ppg=False, **post):
        """
        Return all incomes
        """
        if ppg:
            try:
                ppg = int(ppg)
            except ValueError:
                ppg = PPG
            post["ppg"] = ppg
        else:
            ppg = PPG
        income_summary = request.env['income.summary']
        domain = [('date','<=',fields.Date.today())]
        income_ids = income_summary.search(domain, order=post.get('order'))
        inc_catg_ids = request.env['income.category'].search([]).mapped('name')
        account_id_list = request.env['bank.account'].search([]).mapped('name')
        account_ids = ','.join(account_id_list)
        pager = mypager(self, url='/my_incomes', total=len(income_ids), page=page, step=ppg)
        offset = pager['offset']
        income_ids = income_ids[offset: offset + ppg]
        values = {
                    'my_incomes': income_ids,
                    'catg_ids' : inc_catg_ids,
                    'accounts' :account_id_list,
                    'pager':pager,
                 }
        return request.render("budget_expense_management.portal_my_incomes", values)

    @http.route('/my_incomes', type='json', auth="user", website=True, methods=['DELETE'],  csrf=False)
    def delete_expense(self, **kwargs):
        """
        Delete income pointed by income_id
        """
        data = json.loads(request.httprequest.data.decode('utf-8'))
        if 'income_id' in data:
            income_summary = request.env['income.summary'] 
            record_to_delete = income_summary.browse(data['income_id']).unlink()

        return Response("success", status=200)

    @http.route('/my_incomes', type='json', auth="user", website=True, methods=['PATCH'],  csrf=False)
    def update_income(self, **kwargs):
        """
        Delete income pointed by income_id
        """
        try:
            data = json.loads(request.httprequest.data.decode('utf-8'))
            inc_id = request.env['income.summary'].browse([int(data['inc_id'])])
            if inc_id:
                if data['date']:
                    date_obj = datetime.strptime(data['date'],'%m/%d/%Y').date()
                    inc_id.date = date_obj.strftime(DF)
                if data['category']:
                    catg_obj = request.env['income.category'].search([('name','=', data['category'])])
                    if catg_obj and catg_obj.name :
                        inc_id.exp_category_id = catg_obj.id
                if data['description']:
                    inc_id.name = data['description']
                if data['account']:
                    account_obj = request.env['bank.account'].search([('name','=', data['account'])])
                    if account_obj and account_obj.name :
                        inc_id.account_journal_id = account_obj.id
                if data['amount']:
                    newdata = data['amount'].replace('$','').replace(',','')
                    inc_id.amount = float(newdata)
        except Exception as exc:
            print(exc)
            Response.status = "400"
            return "Error"
        Response.status = "200"
        return "success"

