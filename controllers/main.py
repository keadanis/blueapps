# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models, http, tools, _
from odoo.http import request, Response
from datetime import timedelta, date, datetime
import calendar
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
import math

# define new pager function to add start and end to expense and income pages
def mypager(self, url, total, page=1, step=30, scope=5, url_args=None):

    # Compute Pager
    page_count = int(math.ceil(float(total) / step))

    page = max(1, min(int(page if str(page).isdigit() else 1), page_count))
    scope -= 1

    pmin = max(page - int(math.floor(scope/2)), 1)
    pmax = min(pmin + scope, page_count)
    if pmax - pmin < scope:
        pmin = pmax - scope if pmax - scope > 0 else 1

    def get_url(page):
        _url = "%s/page/%s" % (url, page) if page > 1 else url
        if url_args:
            _url = "%s?%s" % (_url, urls.url_encode(url_args))
        return _url
    return {
        "budget": True,
        "start": get_url(1),
        "end":get_url(page_count),
        "page_count": page_count,
        "offset": (page - 1) * step,
        "page": {
            'url': get_url(page),
            'num': page
        },
        "page_start": {
            'url': get_url(pmin),
            'num': pmin
        },
        "page_previous": {
            'url': get_url(max(pmin, page - 1)),
            'num': max(pmin, page - 1)
        },
        "page_next": {
            'url': get_url(min(pmax, page + 1)),
            'num': min(pmax, page + 1)
        },
        "page_end": {
            'url': get_url(pmax),
            'num': pmax
        },
        "pages": [
            {'url': get_url(page_num), 'num': page_num} for page_num in range(pmin, pmax+1)
        ]
    }


class BudgetMonthlyReport(http.Controller):
    
    def _get_spent_expense(self, first_day,last_day):
        categ_dict = {}
        categories = request.env['expense.category'].sudo().search([])
        budgeted_exp_id =  request.env['budgeted.expense'].sudo().search([('date_from','>=',first_day),
                                                                ('date_to','<=',last_day)])
        for categ in categories:
            sum =0
            budgtd_exp_categ_id = request.env['budget.expense.lines'].search([('budgeted_id','=',budgeted_exp_id.id), 
                                                                              ('category_id','=',categ.id)])
            expenses = request.env['expense.summary'].search([
                                                              ('date','>=', first_day),
                                                              ('date','<=', last_day),
                                                              ('exp_category_id','=',categ.id)])
            for exp in expenses:
                sum += exp.amount
            if sum == 0:
                continue
                
            categ_dict.update({categ:{'spent':sum or 0, 'budgeted': budgtd_exp_categ_id.amount or 0}})
        return categ_dict
    
    def get_all_months(self):
        month = ['January','February','March','April','May','June',
                 'July','August','September','October','November','December']
        return month
        

    def get_income(self, first_day,last_day):
        inc_categ_dict = {}
        inc_category_ids = request.env['income.category'].sudo().search([])
        exp_income_monthly_id = request.env['expected.income'].search([('date_from','>=',first_day),
                                                                ('date_to','<=',last_day)])
        for inc_categ in inc_category_ids:
            sum = 0
            expected_inc_categ_id = request.env['expected.income.line'].search([('exp_income_id','=',exp_income_monthly_id.id), 
                                                                              ('category_id','=',inc_categ.id)])
            income_ids = request.env['income.summary'].search([
                                                          ('date','>=', first_day),
                                                          ('date','<=', last_day),
                                                          ('income_categ_id','=',inc_categ.id)])
            for inc in income_ids:
                sum += inc.amount
            if sum == 0:
                continue
            inc_categ_dict.update({inc_categ:{'actual':sum or 0, 'planned': expected_inc_categ_id.line_amount or 0}})
        return inc_categ_dict
        
    def get_account_details(self, first_day, last_day):
        account_dict = {}
        account_ids = request.env['bank.account'].sudo().search([])
        for acct in account_ids:
            sum = 0
            request.env.cr.execute("""select sum(amount) from expense_summary where date >= %s AND
                            date <= %s AND account_journal_id = %s AND
                            user_id=%s""",
                             ((first_day, last_day, acct.id, request.env.user.id)))
            exp =request.env.cr.dictfetchall() 
            current_balance = acct.account_balance(acct, last_day)
            if not exp[0]['sum'] and not current_balance:
                continue
            
            account_dict.update({acct: {'amt_spent': exp[0]['sum'] or 0, 'balance':current_balance or 0}})
        return account_dict   
     
     
    def get_monthly_investment(self, first_day, last_day):
        accounts = request.env['bank.account'].sudo().search([('type','=','investment')])
        sum = 0
        for acct in accounts:
            debit, credit = acct.amount_transfered(acct, first_day, last_day)
            sum += (credit or 0)
            sum -= (debit or 0)
        return sum
            
    @http.route('/budget_monthly_rpt/', type = 'http', auth='user', methods=['GET'], website=True)
    def render_budget_monthly_rpt(self, **kwargs):
        vals = {}
        month = ['January','February','March','April','May','June',
                 'July','August','September','October','November','December']
        years = []
        year_ids = request.env['budget.year'].sudo().search([])
        for year in year_ids:
            years.append(year.name)
        today = fields.Date.today()
        if 'current_month' in request.httprequest.args or 'current_year' in request.httprequest.args:
            current_month = request.httprequest.args['current_month']
            current_year = request.httprequest.args['current_year']
            first_day = datetime.strptime(current_month, '%B').replace(year=int(current_year),day=1).date()
            last_day_of_month = calendar.monthrange(int(current_year), first_day.month)[1]
            last_day = date(int(current_year), first_day.month, last_day_of_month)
        else:
            current_month = today.strftime('%B')
            current_year = today.year
            first_day = date(int(current_year), today.month, 1)
            last_day_of_month = calendar.monthrange(int(current_year), today.month)[1]
            last_day = date(int(current_year), today.month, last_day_of_month)
        vals = {'month': self.get_all_months(),
                     'current_month': current_month,
                     'years':years,
                     'current_year': current_year,
                     'exp_categories': self._get_spent_expense(first_day,last_day),
                     'income_details': self.get_income(first_day,last_day),
                     'account_details': self.get_account_details(first_day, last_day),
                     'investment': self.get_monthly_investment(first_day, last_day),
                     'currency': request.env.user.currency_id}
        
        return request.render("budget_expense_management.budget_montly_report_template", vals)
    
    
    @http.route('/cash_transfer', type='http',methods=['GET'], auth='user', website=True)
    def transfer_cash_form(self, **kwargs):
        accounts = request.env['bank.account'].sudo().search([])
        return request.render("budget_expense_management.cash_transfer_template",
                              { 'accounts': accounts })

    @http.route('/cash_transfer', type='http',methods=['POST'], auth='user', website=True, csrf=False)
    def transfer_cash(self, **post):
        account_transfer = request.env['account.money.transfer']
        account_transfer_id = account_transfer.create({
                    'name':post.get('note', False),
                    'date':post.get('date', False),
                    'source_journal_id':post.get('source_account', False),
                    'dest_journal_id':post.get('destination_account', False),
                    'amount':post.get('amount', False),
                    
        })
        return Response("success", status=200)
    
    def get_first_and_last_day(self, month, year):
        today = fields.Date.today()
        month_no = datetime.strptime(month, "%B").month
        first_day = date(year, month_no, 1)
        last_day_of_month = calendar.monthrange(year, month_no)[1]
        last_day = date(year, month_no, last_day_of_month)
        return first_day, last_day
    
    def net_worth(self):
        account_ids = request.env['bank.account'].sudo().search([])
        today = fields.Date.today()
        current_balance = 0
        for acct in account_ids:
            current_balance += acct.account_balance(acct, today)
        return round(current_balance)
    
    def account_sum(self, investment_acc=True):
        today = fields.Date.today()
        if investment_acc:  
            account_ids = request.env['bank.account'].sudo().search([('type', '=', 'investment')])
        else:
            account_ids = request.env['bank.account'].sudo().search([('type', '!=', 'investment'),
                                                                     ('type', '!=', 'loan')])
        current_balance = 0
        for acct in account_ids:
            current_balance += acct.account_balance(acct, today)
        return round(current_balance)   
        
    
    def total_summary(self, year):
        months = self.get_all_months()
        income_list = []
        expense_list = []
        savings_list= []
        income_sum = 0
        expense_sum = 0
        savings_sum = 0
        total_summary = {}
        total_summary['Income'] = ()
        total_summary['Expense'] = ()
        total_summary['Net Savings'] = ()
        
        for month in months:
            first_day, last_day = self.get_first_and_last_day(month, year)
            monthly_income = self.get_income(first_day,last_day)
            monthly_expense = self._get_spent_expense(first_day,last_day)
            monthly_inc = 0
            monthly_exp = 0
            inc_categ_monthly_sum = 0
            inc_summ_list = []
            for inc in monthly_income:
                actual = monthly_income[inc]['actual']
                monthly_inc += actual
            income_list.append(round(monthly_inc))
            for exp in monthly_expense:
                monthly_exp += monthly_expense[exp]['spent']
            expense_list.append(round(monthly_exp))
            savings_list.append(round(monthly_inc - monthly_exp))
        for inc in income_list:
            income_sum += inc
            
        for exp in expense_list:
            expense_sum += exp   
        for savings in savings_list:
            savings_sum += savings         
        total_summary['Income'] = (income_list, round(income_sum), round(income_sum/12))
        total_summary['Expense'] = (expense_list, round(expense_sum), round(expense_sum/12))
        total_summary['Net Savings'] = (savings_list, round(savings_sum), round(savings_sum/12))
        
        return total_summary 
   
    def annual_income_summary(self, year):
        months = self.get_all_months()
        inc_categ_ids = request.env['income.category'].sudo().search([])
        income_summary = {}
        for inc in inc_categ_ids:
            inc_summ_list = []
            income_sum = 0
            for month in months:
                sum =0
                first_day, last_day = self.get_first_and_last_day(month, year)
                income_ids = request.env['income.summary'].search([
                                                          ('date','>=', first_day),
                                                          ('date','<=', last_day),
                                                          ('income_categ_id','=',inc.id)])
                for inc_id in income_ids:
                    sum += inc_id.amount
                inc_summ_list.append(round(sum))
            for monthly_income in inc_summ_list:
                income_sum += monthly_income
            income_summary.update({inc.name: (inc_summ_list, income_sum, round(income_sum/12))})
        return income_summary
    
    def annual_investment_summary(self, year):
        months = self.get_all_months();
        
        inv_total = ()
        investment_list = []
        total_investment = 0
        for month in months:
            first_day, last_day = self.get_first_and_last_day(month, year)
            invest_per_month = self.get_monthly_investment(first_day, last_day)
            investment_list.append(round(invest_per_month))
            total_investment += invest_per_month
        return {'Investment':  (investment_list, round(total_investment), round(total_investment/12))}
    
    def annual_expense_summary(self, year):
        months = self.get_all_months()
        exp_categ_ids = request.env['expense.category'].sudo().search([])
        expense_summary = {}
        
        for exp in exp_categ_ids:
            exp_summ_list = []
            expense_sum = 0
            for month in months:
                sum =0
                first_day, last_day = self.get_first_and_last_day(month, year)
                expense_ids = request.env['expense.summary'].search([
                                                              ('date','>=', first_day),
                                                              ('date','<=', last_day),
                                                              ('exp_category_id','=',exp.id)])
                for exp_id in expense_ids:
                    sum += exp_id.amount
                exp_summ_list.append(round(sum))
            for monthly_expense in exp_summ_list:
                expense_sum += monthly_expense
            expense_summary.update({exp.name: (exp_summ_list, expense_sum, round(expense_sum/12))})
        return expense_summary

    @http.route('/annual_summary/', type = 'http', auth='user', methods=['GET'], website=True)
    def annual_summary(self, **kwargs):
        today = fields.Date.today()
        year = request.env['budget.year'].search([]).mapped('name')
        current_year =  today.year
        if  'current_year' in request.httprequest.args:
            current_year = int(request.httprequest.args['current_year'])
        vals = {
            'summary':self.total_summary(current_year),
            'income_summary': self.annual_income_summary(current_year),
            'expense_summary' : self.annual_expense_summary(current_year),
            'year' : year,
            'investment_summary': self.annual_investment_summary(current_year),
            'current_year': current_year,
            'currency': request.env.user.currency_id,
            'net_worth': self.net_worth(),
            'investment_total': self.account_sum(),
            'savings_total': self.account_sum(investment_acc=False)
            }
        return request.render("budget_expense_management.annual_summary_report_template", vals)
