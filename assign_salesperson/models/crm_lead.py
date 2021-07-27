from odoo import models, api, fields

class CrmLead(models.Model):
    
    _inherit = 'crm.lead'

    # @api.multi
    # def write(self, vals):
    #     res = super(CrmLead, self).write(vals)
    #     if vals.get('user_id'):
    #         welcome_email_template = self.env.ref('assign_salesperson.email_template_welcome_email')
    #         for rec in self:
    #             welcome_email_template.send_mail(rec.id, force_send=True)
    #     return res