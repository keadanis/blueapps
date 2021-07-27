# -*- coding: utf-8 -*-

import logging

from datetime import datetime, timedelta, date
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)


class Contract(models.Model):
    _inherit = 'hr.contract'
    _order = 'registration_date desc,create_date desc, id desc'

    team_id = fields.Many2one('crm.team', 'Team', index=True)
    type_doc = fields.Selection([
        ('ctt_ett', 'Contract Ett'),
        ('ctt_employee', 'Contract Employee')], 'Type Document', track_visibility='always', default=lambda self: self._context.get('type_doc', 'ctt_ett'))
    partner_id = fields.Many2one('res.partner', 'Client', track_visibility='onchange', index=True)
    quotation_id = fields.Many2one('sale.order', 'Ref order', track_visibility='onchange', index=True)
    employee_id = fields.Many2one('hr.employee', 'Employee', track_visibility='onchange', index=True)
    doc_ident = fields.Char('DNI/NIE/Pas.')
    job_seeker = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')], 'Demandante Empleo', track_visibility='onchange')
    contract_hours = fields.Char('Contract hours')
    cc_nass_code = fields.Char('Code NASS')
    cc_nass_number = fields.Char('No. NASS')
    abred_code = fields.Char('Code ABRED', default='N')
    notification_inem = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')], 'Notification INEM', track_visibility='onchange')
    code_inem = fields.Char('Category SEPE', help='Code number of SEPE job category')
    type_retribution = fields.Char('Type retribution')
    registration_date = fields.Date('Registration', index=True, help='Date of registration of the contract')
    termination_date = fields.Date('Termination', index=True, help='Date of termination of the contract')
    agreement_id = fields.Many2one('collective.agreement', 'Collective agreement', track_visibility='onchange', index=True)
    category_professional_id = fields.Many2one('formation.category.professional', 'Professional category', track_visibility='onchange', index=True)
    cotization_id = fields.Many2one('formation.cotization.group', 'Cotization group', track_visibility='onchange', index=True)
    educational_level_id = fields.Many2one('formation.educational.level', 'Educational level', track_visibility='onchange', index=True)
    termination_cause = fields.Selection([
            ('v', 'Contract variation'),
            ('f', 'Contract end'),
            ('e', 'Test not superated for company'),
            ('t', 'Test not superated for employee'),
            ('c', 'Recess voluntary'),
            ('s', 'Labor strike'),
            ('a', 'Abandonment')], 'Baja/Cause termination', track_visibility='onchange')
    ctt_assumption = fields.Selection([
            ('1', 'Obre'),
            ('2', 'Acumulation'),
            ('3', 'Sustitution'),
            ('4', 'Selection'),
            ('5', 'Formation'),
            ('6', 'Practics')], 'Assumption', track_visibility='onchange')
    obj_control_ctto = fields.Text('Object ctto')
    formation_job_id = fields.Many2one('formation.job', 'Job', track_visibility='onchange', index=True)
    cif_client = fields.Char('CIF')
    state = fields.Selection([
        ('draft', 'New'),
        ('open', 'Running'),
        ('valid', 'Valid'),
        ('done', 'Done'),
        ('cancel', 'Cancel'),
        ('pending', 'To Renew'),
        ('close', 'Expired'),
    ], string='Status', track_visibility='onchange', help='Status of the contract', default='draft')
    accom = fields.Integer('Accommodation')
    trans = fields.Integer('Transportation')
    mobi = fields.Integer('Mobile')
    food = fields.Integer('Food')
    nature = fields.Integer('Nature Of Work')
    time_execution = fields.Datetime('Management SS', help='Creation/ Update registers')
    registration_finger = fields.Char('Registration finger')
    termination_finger = fields.Char('Termination finger')

    @api.model
    def create(self, vals):
        contract = super(Contract, self).create(vals)
        if contract.type_doc == 'ctt_ett':
            if contract.name and contract.team_id:
                contract.name = 'Cto' + '-' + contract.team_id.name + '-' +  contract.name
        return contract

    def action_request_registration(self):
        if self.filtered(lambda obj_contract: obj_contract.state == 'draft'):
            # if not self.registration_date or not self.date_start:
            #     raise UserError(_('The date registration date the contract or incorporation cannot be empty.'))
            self.write({'state': 'valid', 'abred_code': 'A', 'time_execution': self.write_date})
            employee = self.mapped('employee_id')
            if employee:
                employee.write({'is_hired': True})
            if self.termination_date:
                employee.write({'date_last_b': self.termination_date})

    def action_approve(self):
        if self.filtered(lambda obj_contract: obj_contract.state == 'valid'):
            # if not self.termination_date or not self.date_end:
            #     raise UserError(_('The termination date the contract or finish cannot be empty.'))
            self.write({'state': 'done', 'abred_code': 'AB', 'time_execution': self.write_date})
            employee = self.mapped('employee_id')
            if employee:
                employee.write({'is_hired': False})
            if self.termination_date:
                employee.write({'date_last_b': self.termination_date})

    def action_disapprove(self):
        if self.filtered(lambda obj_contract: obj_contract.state in ['done', 'valid', 'draft']):
            self.write({'state': 'cancel', 'abred_code': 'C', 'time_execution': self.write_date})
            employee = self.mapped('employee_id')
            if employee:
                employee.write({'is_hired': False})
            if self.termination_date:
                employee.write({'date_last_b': self.termination_date})

    def action_reset_to_new(self):
        if self.filtered(lambda obj_contract: obj_contract.state in ['cancel', 'done', 'valid']):
            self.write({'state': 'draft', 'abred_code': 'C', 'time_execution': self.write_date})
            employee = self.mapped('employee_id')
            if employee:
                employee.write({'is_hired': False})
            if self.termination_date:
                employee.write({'date_last_b': self.termination_date})


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_employee = fields.Boolean(string='Employee', help="Check this box if this contact is a Employee.")


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    pnafss = fields.Char('PNAFSS')
    nafss = fields.Char('NAFSS')
    fv_nie = fields.Date('DNI/NIE Caduc.')
    irpf_cuote = fields.Float('Quote IRPF', help='Quote IRPF')
    irpf_base = fields.Float('Base IRPF', help='Base IRPF')
    irpf_personal = fields.Float('Personal IRPF', help='Min personal IRPF')
    date_last_b = fields.Date('Fecha baja', help='Last date')
    category_professional_id = fields.Many2one('formation.category.professional', 'Professional category', track_visibility='onchange', index=True)
    cotization_id = fields.Many2one('formation.cotization.group', 'Cotization group', track_visibility='onchange', index=True)
    educational_level_id = fields.Many2one('formation.educational.level', 'Educational level', track_visibility='onchange', index=True)
    formation_job_id = fields.Many2one('formation.job', 'Job', track_visibility='onchange', index=True)
    empl_ett = fields.Boolean('Employee ETT', track_visibility='always', default=lambda self: self._context.get('empl_ett', True))
    is_hired = fields.Boolean('Hired', track_visibility='onchange', default=False)

    @api.model
    def create(self, vals):
        employee = super(HrEmployee, self).create(vals)
        if self._context.get('empl_ett'):
            employee.empl_ett = self._context.get('empl_ett')
        else:
            employee.empl_ett = self._context.get('empl_ett')
        return employee


class FormationCategoryProfessional(models.Model):
    _name = 'formation.category.professional'
    _description = 'Category Professional'

    name = fields.Char('Name', index=True, required=True)
    description = fields.Char('Description')


class FormationCotizationGroup(models.Model):
    _name = 'formation.cotization.group'
    _description = 'Cotization Group'

    name = fields.Char('Name', index=True, required=True)
    description = fields.Char('Description')


class FormationEducationalLevel(models.Model):
    _name = 'formation.educational.level'
    _description = 'Educational Level'

    name = fields.Char('Name', index=True, required=True)
    description = fields.Char('Description')


class FormationJob(models.Model):
    _name = 'formation.job'
    _description = 'Job'
    _order = 'name asc'

    name = fields.Char('Name', index=True, required=True)
    description = fields.Char('Description')


class CollectiveAgreement(models.Model):
    _name = 'collective.agreement'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = 'Collective Agreement'
    _order = 'create_date desc'

    name = fields.Char('Number', index=True, required=True)
    code = fields.Char(required=True, copy=False)
    partner_id = fields.Many2one('res.partner', string='Partner', ondelete='restrict', domain=[('parent_id', '=', False)])
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env['res.company']._company_default_get())
    contract_hours = fields.Char('Contract hours')
    net_salary = fields.Float('Salary net')
    brut_salary = fields.Float('Salary brut')
    description = fields.Text('Description')
    category_professional_id = fields.Many2one('formation.category.professional', 'Professional category', track_visibility='onchange', index=True)
    cotization_id = fields.Many2one('formation.cotization.group', 'Cotization group', track_visibility='onchange', index=True)
    educational_level_id = fields.Many2one('formation.educational.level', 'Educational level', track_visibility='onchange', index=True)
    formation_job_id = fields.Many2one('formation.job', 'Job', track_visibility='onchange', index=True)
    tag_cnae_id = fields.Many2one('tag.cnae.category', 'CNAE', index=True, track_visibility='onchange', help='Groups CNAE.')
    sector_cnae = fields.Many2one('tag.ine.category', 'Sector', track_visibility='onchange')
    attachment_ids = fields.Many2many('ir.attachment', 'attact_efirm_rel', 'efirm_id', 'attach_id', ondelete="cascade", string='Attachments')
    term_description = fields.Html('Term description')
    is_template = fields.Boolean("Is a Template?", default=False, copy=False, help="Set if the agreement is a template. Template agreements don't require a partner.")
    agreement_id = fields.Many2one('collective.agreement', 'Collective agreement', track_visibility='onchange', index=True)
    type_id = fields.Many2one('agreement.type', 'Agreement type', track_visibility='onchange', index=True)
    active = fields.Boolean(default=True)
    signature_date = fields.Date()
    start_date = fields.Date()
    end_date = fields.Date()

    def name_get(self):
        res = []
        for agr in self:
            name = agr.name
            if agr.code:
                name = '[%s] %s' % (agr.code, agr.name)
            res.append((agr.id, name))
        return res

    _sql_constraints = [('code_partner_company_unique', 'unique(code, partner_id, company_id)', 'This agreement code already exists for this partner!')]


class AgreementType(models.Model):
    _name = "agreement.type"
    _description = "Agreement Types"

    name = fields.Char(string="Name", required=True)
    active = fields.Boolean(default=True)


class TagCategoryCNAE(models.Model):
    _name = 'tag.cnae.category'
    _description = 'Categories CNAE'

    name = fields.Char('Name', required=True, index=True)
    code_cnae = fields.Char('Code')
    active = fields.Boolean('Active', default='True')
    code_general = fields.Boolean('General')
    parent_id = fields.Many2one('tag.cnae.category', 'Parent')
    category_ine_id = fields.Many2one('tag.ine.category', 'INE')
    note = fields.Text('Notes')

    # heredo el create para modificar name
    @api.model
    def create(self, vals):
        request = super(TagCategoryCNAE, self).create(vals)
        code_cnae = request.code_cnae
        if request.name:
            request.name = code_cnae + ' - ' + request.name
        if not request.category_ine_id:
            obj_ine_tag = self.env['tag.ine.category'].search([('active', '=', True)])
            for obj_ine in obj_ine_tag:
                code_ine = obj_ine.code_ine
                code_spl = code_ine.replace(" ", "").split(',')
                if code_cnae in code_spl:
                    request.category_ine_id = obj_ine.id
        if len(code_cnae) > 2:
            if len(code_cnae) == 4:
                request.code_general = 'True'
                cont_min = code_cnae[:3]
            elif len(code_cnae) == 3:
                cont_min = code_cnae[:2]
            obj_tag = self.env['tag.cnae.category'].search([('code_cnae', '=', cont_min)])
            for obj in obj_tag:
                request.parent_id = obj.id
        if len(code_cnae) == 2:
            list_cnae = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U']
            obj_tag = self.env['tag.cnae.category'].search([('code_cnae', 'in', list_cnae)])
            for obj in obj_tag:
                request.parent_id = obj.id
        return request

    # heredo el write para modificar name
    def write(self, vals):
        if vals and 'code_cnae' in vals:
            code_cnae = vals.get('code_cnae')
            if len(code_cnae) > 2:
                if len(code_cnae) == 4:
                    self.code_general = 'True'
                    cont_min = code_cnae[:3]
                elif len(code_cnae) == 3:
                    self.code_general = 'False'
                    cont_min = code_cnae[:2]
                obj_tag = self.env['tag.cnae.category'].search([('code_cnae', '=', cont_min)])
                for obj in obj_tag:
                    self.parent_id = obj.id
            if len(code_cnae) == 2:
                self.code_general = 'False'
                list_cnae = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U']
                obj_tag = self.env['tag.cnae.category'].search([('code_cnae', 'in', list_cnae)])
                for obj in obj_tag:
                    self.parent_id = obj.id
        res = super(TagCategoryCNAE, self).write(vals)
        return res


class TagCategoryINE(models.Model):
    _name = 'tag.ine.category'
    _description = 'Categories INE'

    name = fields.Char('Name', required=True, index=True)
    code_ine = fields.Char('Code')
    active = fields.Boolean('Active', default='True')
    note = fields.Text('Notes')


class SaleOrder(models.Model):
    _inherit = "sale.order"

    agreement_id = fields.Many2one('collective.agreement', 'Collective Agreement', track_visibility='onchange')
    check_process = fields.Boolean('Process', default=False)
    count_create = fields.Integer('Created')
    count_pending = fields.Integer('Pending')

    def action_create_contract(self):
        for obj_sale in self:
            count_empl = 0
            count_line = 0
            val_default = '00'
            create_contract = self.env['hr.contract']
            if obj_sale.state == 'sale':
                qty_delivered = 0
                if obj_sale.mapped('agreement_id'):
                    agreement = obj_sale.mapped('agreement_id')
                    agreement_id = agreement.id
                    category_id = agreement.category_professional_id.id
                    cotization_id = agreement.cotization_id.id
                    level_id = agreement.educational_level_id.id
                    agreement_hours = agreement.contract_hours
                    agreement_wage = agreement.net_salary
                    job_id = agreement.formation_job_id.id
                if obj_sale.team_id:
                    team = obj_sale.team_id.id
                if obj_sale.partner_id:
                    partner = obj_sale.partner_id.id
                    vat = obj_sale.partner_id.vat
                obj_lines = self.mapped('order_line')
                for line in obj_lines:
                    count_line += 1
                    if line.qty_delivered:
                        qty_delivered += int(line.qty_delivered)
                        count_create = qty_delivered
                    else:
                        raise UserError(_('To create a contract you must review the delivered quantity of your order lines.'))
                while qty_delivered > 0:
                    obj_employee_id = self.env['hr.employee'].search([('category_professional_id', '=', category_id), ('cotization_id', '=', cotization_id), ('educational_level_id', '=', level_id), ('formation_job_id', '=', job_id), ('is_hired', '=', False)])
                    if obj_employee_id:
                        count_free = len(obj_employee_id)
                        count_pending = count_create - count_free
                        if count_free <= qty_delivered:
                            qty_delivered = count_free
                            count_pending = 0
                        else:
                            obj_employee_id = obj_employee_id[qty_delivered:]
                        while qty_delivered > 0:
                            for obj_employee in obj_employee_id:
                                count_empl += 1
                                employee = obj_employee.id
                                doc_ident = obj_employee.identification_id
                                val_default = doc_ident[1:5]
                                new_order = val_default + '-' + str(count_line) + str(count_empl)
                                dict_contract = {
                                    'name': new_order,
                                    'team_id': team,
                                    'agreement_id': agreement_id,
                                    'category_professional_id': category_id,
                                    'cotization_id': cotization_id,
                                    'educational_level_id': level_id,
                                    'type_doc': 'ctt_ett',
                                    'partner_id': partner,
                                    'quotation_id': obj_sale.id,
                                    'employee_id': employee,
                                    'contract_hours': agreement_hours,
                                    'wage': agreement_wage,
                                    'doc_ident': doc_ident,
                                    'cif_client': vat,
                                }
                                create_contract.create(dict_contract)
                                qty_delivered -= 1
                                obj_employee.write({'is_hired': True})
                        obj_sale.write({'check_process': True, 'count_create': count_create, 'count_pending': count_pending})
                    else:
                        raise UserError(_('There are no employees available to hire. You can contact your manager or open a new recruitment process.'))
        return False
