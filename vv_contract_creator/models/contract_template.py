from odoo import models, fields, _


class ContractTemplate(models.Model):
    _name = 'vv.contract.template'
    _description = 'Contract Templates'

    name = fields.Char('Name')
    template = fields.Html('Contract Template')

    _sql_constraints = [
        ('unique_name', 'UNIQUE(name)',
         _('Contract Template with this specified Name is already exist !')),
    ]
