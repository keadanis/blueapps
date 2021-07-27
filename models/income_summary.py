from odoo import api, fields, models, tools

class IncomeSummary(models.Model):
    _name = 'income.summary'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Income Summary'
    _order = 'date desc'
    
    name = fields.Char('Description',track_visibility="onchange")
    date = fields.Date('Date',track_visibility="onchange")
    amount = fields.Float('Amount',track_visibility="onchange")
    income_categ_id = fields.Many2one('income.category', string='Category',track_visibility="onchange")
    account_journal_id = fields.Many2one('bank.account', string='Account',track_visibility="onchange",auto_join=True,ondelete='cascade')
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.user.currency_id)
    investment_id =  fields.Many2one('investment.interest', 'Investment Ref')
    
    
       