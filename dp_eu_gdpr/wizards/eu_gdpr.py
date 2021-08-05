# -*- coding: utf-8 -*-
# Copyright 2018-Today datenpol gmbh (<http://www.datenpol.at>)
# License OPL-1 or later (https://www.odoo.com/documentation/user/13.0/legal/licenses/licenses.html#licenses).

import base64
import csv
import re
import zipfile
from io import BytesIO, StringIO

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class EuGdpr(models.TransientModel):
    _name = 'eu.gdpr'
    _description = 'GDPR Wizard'

    @api.model
    def selections(self):
        # Check for installed modules and append them to the Data Set selection
        selections = []
        for rec in self._gdpr_objects():
            model = self.with_context(lang=self.env.user.lang).env['ir.model'].search([('model', '=', rec)])
            if model:
                selections.append((model.model, model.name))
                self._check_access_rights(rec)
        return selections

    operation = fields.Selection([
        ('access', _('Right to data portability')),
        ('erasure', _('Right to erasure')),
        ('rectification', _('Right to rectification')),
        ('restrict', _('Right to restriction of processing')),
    ], 'Operation', default='access', required=True)
    object = fields.Reference(selections, 'Data Set')
    partner = fields.Char('Inquiring Partner', help='Person who executed the operation (e. g. Customer)')
    note = fields.Text('Notes')
    info = fields.Text('Info', readonly=True, help='Display the result of operation.')
    help = fields.Char('Helptext', readonly=True)

    @api.onchange('operation')
    def _onchange_operation(self):
        for record in self:
            if record.operation == 'access':
                record.help = _('A compressed ZIP file will be created, which provides the data in an CSV file.')

            elif record.operation == 'erasure':
                record.help = _('WARNING: Please note the legal record retention and the attainment of an aim. '
                                'If one of the two cases occurs, the operation must not be performed. '
                                'Individual-related data will be deleted. If that is not possible, due to technical '
                                'difficulties, the data will be set to inactive instead and will be replaced '
                                'by pseudonyms. Also related data sets, that reference this data, will be deleted - '
                                'e.g. partner of user or user of employee. '
                                'Examples for the legal record retention: Accounting, tax and customs law: 7 - 22 years'
                                ', HR: 2 - 30 years')

            elif record.operation == 'rectification':
                record.help = _('No operation will be executed from here - it has to be done manually. Regardless '
                                'a GDPR log entry will be created.')

            elif record.operation == 'restrict':
                record.help = _('Set individual-related data to inactive.')

            else:
                record.help = ''

    @api.onchange('object')
    def _onchange_object(self):
        if self.operation == 'erasure' and self.object:
            self._partner_is_company()

    @api.model
    def _check_access_rights(self, model):
        """
        Create access rights for the gdpr group for the specified model, if it doesn't have access yet.
        """
        xml_id_name = 'access_eu_gdpr_' + model.replace('.', '_')
        xml_ids = self.env['ir.model.access'].search([('name', '=', xml_id_name)])
        if not xml_ids:
            self.env['ir.model.access'].create({
                'name': xml_id_name,
                'model_id': self.env['ir.model'].search([('model', '=', model)]).id,
                'group_id': self.env.ref('dp_eu_gdpr.dp_eu_gdpr_user').id,
                'perm_create': False,
                'perm_read': True,
                'perm_write': True,
                'perm_unlink': True,
            })

    @api.model
    def _gdpr_objects(self):
        """
        Return models, that the gdpr app has to consider.
        """
        return ['crm.lead', 'res.partner', 'res.users', 'hr.employee', 'hr.applicant']

    def _personal_fields_crm_lead(self):
        return [
            'name', 'partner_id', 'email_from', 'phone', 'partner_name',
            'street', 'street2', 'city', 'state_id', 'zip', 'country_id',
            'contact_name', 'title', 'function', 'mobile', 'website',
        ]

    def _personal_fields_res_partner(self):
        return [
            'name', 'street', 'street2', 'city', 'zip', 'country_id',
            'function', 'phone', 'mobile', 'email', 'title', 'lang',
            'website', 'state_id',
        ]

    def _overwrite_fields_res_partner_bank(self):
        return ['acc_number']

    def _personal_fields_res_partner_bank(self):
        return ['acc_number']

    def _personal_fields_res_users(self):
        return [
            'name', 'login', 'partner_id', 'signature',
        ]

    def _personal_fields_hr_applicant(self):
        return [
            'name', 'partner_name', 'partner_id', 'type_id', 'email_from',
            'partner_phone', 'partner_mobile', 'salary_expected',
        ]

    def _personal_fields_hr_employee(self):
        res = [
            'name', 'country_id', 'identification_id', 'passport_id',
            'bank_account_id', 'gender', 'marital', 'address_home_id',
            'birthday', 'user_id', 'work_email', 'visa_no', 'permit_no',
            'visa_expire',
        ]

        domain = [
            ('name', '=', 'hr_contract'),
            ('state', '=', 'installed'),
        ]
        if self.env['ir.module.module'].search_count(domain):
            res.extend([
                'place_of_birth',
                'children',
            ])

        return res

    def _update_wizard(self, message):
        self.write({'object': False, 'info': message})

    def process(self):
        if not self.object:
            raise ValidationError(_('You need to specify a data set.'))

        vals = self._prepare_log()
        log = self.env['eu.gdpr_log'].sudo().create(vals)
        res = self._reload_wizard_properties()

        if self.operation == 'access':
            att_id = self._export_csv(log)
            res.update({
                'type': 'ir.actions.act_url',
                'url': '/web/content/%s?download=true' % att_id,
                'target': 'current',
            })

        elif self.operation == 'erasure':
            self._check_restrictions()
            current_seq = self.env['ir.sequence'].next_by_code('gdpr')

            # self._process_delete will return True if deletion was successful
            # and no pseudomization was needed.
            no_pseudomize = self.with_context(current_seq=current_seq)._process_delete(self.object)

            if no_pseudomize:
                self._update_wizard(_('The object was successfully deleted.'))
            else:
                self._update_wizard(_('The object or sub-objects could not be deleted. '
                                      'Objects were pseudonymized with the number %s.') % current_seq)

        elif self.operation == 'rectification':
            self._update_wizard(_('GDPR Log entry created. Data remains unchanged.'))

        elif self.operation == 'restrict':
            self._process_restriction(self.object)
            self._update_wizard(_('Data Set was set to inactive.'))

        else:
            raise ValidationError(_('You need to specify which type of operation you wish to execute.'))

        return res

    def _prepare_log(self):
        operations = dict(self._fields['operation'].selection)
        objects = dict(dict(self.selections()))
        return {
            'date': fields.Datetime.now(),
            'user_id': self._uid,
            'operation': _(operations.get(self.operation)),
            'object': _(objects.get(self.object._name)),
            'dataset': self.object.name_get()[0][1],
            'partner': self.partner,
            'note': self.note,
        }

    def _reload_wizard_properties(self):
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'eu.gdpr',
            'res_id': self.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def _check_restrictions(self):
        self._partner_is_admin()
        self._partner_is_company()
        self._check_partner_has_invoice()

    def _partner_is_admin(self):
        if self.object._name == 'res.users' and self.object.id == 1:
            raise ValidationError(_('The Administrator cannot be deleted!'))

    def _partner_is_company(self):
        if self.object._name == 'res.partner' and self.object.is_company:
            raise ValidationError(_('Partner is a company and cannot be deleted. Please select a contact.'))

    def _check_partner_has_invoice(self):
        # Check if partner has corresponding invoices
        if self.object._name == 'res.users' and self.pool.get('account.invoice', False):
            invoice_ids = self.env['account.invoice'].search([
                ('partner_id', '=', self.object.partner_id.id), ('state', 'in', ['open', 'paid'])
            ])
            if invoice_ids:
                raise ValidationError(_('Partner cannot be deleted due to corresponding invoices.'))

    def _process_delete_special(self, partner_id):
        # Remove sensitive data from crm.lead on deleting Partner
        CrmLead = self.env.get('crm.lead')
        if CrmLead is not None:
            leads = CrmLead.search([('partner_id', '=', partner_id)])
            vals = {
                'phone': False,
                'contact_name': False,
                'function': False,
                'email_from': False,
                'title': False,
                'mobile': False
            }
            leads.write(vals)

    def _process_restriction(self, obj):
        # Odoo enforces that an user's partner isn't touched. Thus we can't do
        # the normal recursion and need to postpone processing of the partner.
        partner = None
        if obj._name == 'res.users':
            partner = obj.partner_id

        # Recursively restrict objects and related objects
        for field in getattr(self, '_personal_fields_%s' % obj._table)():
            if self._is_recursive(obj, field):
                self._process_restriction(getattr(obj, field))

        if 'active' in obj:
            obj.active = False

        # Postponed processing of an user's partner
        if partner:
            self._process_restriction(partner)

    def _process_delete(self, obj, no_pseudomize=True):
        # no_pseudomize is True by default and will only be set to False if an exception occured.

        # Odoo enforces that an user's partner isn't touched. Thus we can't do
        # the normal recursion and need to postpone processing of the partner.
        partner = None
        if obj._name == 'res.users':
            partner = obj.partner_id

        # Recursively invokes method to make sure that related objects will be deleted as well
        for field in getattr(self, '_personal_fields_%s' % obj._table)():
            if self._is_recursive(obj, field):
                no_pseudomize = self._process_delete(getattr(obj, field))

        if obj._name == 'res.partner':
            self._process_delete_special(obj.id)

        # Precautiously set a savepoint to be able to rollback to that later
        # on in case of an exception
        self._cr.execute('SAVEPOINT page')

        try:
            obj.unlink()
        except Exception:
            # Execution resulted in an exception, which is why we need to
            # return to the savepoint in order to keep Odoo's transaction
            # going.
            self._cr.execute('ROLLBACK TO SAVEPOINT page')

            # Delete all personal fields
            for field in getattr(self, '_personal_fields_%s' % obj._table)():
                # In some models, e.g. res.partner and hr.employee, the name
                # field is not directly required on the model. Thus we would
                # try to clear it. However these models enforce the name via
                # a hidden mechanism, e.g. a SQL CHECK constraint or a related
                # field which has a NOT NULL constraint, and have it required
                # in the view.
                # Thus we can't clear the name. However the field has to
                # remain in the personal fields since we want it to be
                # exported.
                # So it must be ignored here. In the next step it'll be
                # overwritten. In case overwrite fields are defined the name
                # field must be explicitly listed there.
                if field == 'name':
                    continue

                if not obj._fields[field]._description_required:
                    obj.write({field: False})

            overwrite_fields = ['name']
            if '_overwrite_fields_%s' % obj._table in dir(self):
                overwrite_fields = getattr(self, '_overwrite_fields_%s' % obj._table)()

            # Overwrite fields with 'DELETED + sequence'
            for field in overwrite_fields:
                obj.write({field: _('DELETED %s') % self._context.get('current_seq')})

            if 'active' in obj:
                obj.active = False

            # Removing profile picture
            if 'has_image' in obj:
                obj.has_image = False
            if 'image' in obj:
                obj.image = False
            if 'image_small' in obj:
                obj.image_small = False
            if 'image_medium' in obj:
                obj.image_medium = False

            no_pseudomize = False
        finally:
            self._cr.execute('RELEASE SAVEPOINT page')

        # Postponed processing of an user's partner
        if partner:
            res = self._process_delete(partner)
            # If it's already False and processing of the partner succeeds
            # don't reset to True
            if no_pseudomize:
                no_pseudomize = res

        return no_pseudomize

    def _is_recursive(self, obj, field):
        # Odoo doesn't allow to touch the partner while the user still exists.
        # That has to be postponed, thus we ignore it here.
        if (obj._name == 'res.users') and (field == 'partner_id'):
            return False

        # Check if field is an instance of type 'Many2one'
        model = self.env['ir.model.fields'].search([('model', '=', obj._name), ('name', '=', field)])
        if model.ttype == 'many2one' and model.relation in ['res.partner', 'res.users', 'res.partner.bank'] \
                and getattr(obj, field) and getattr(obj, field).id != False:
            return True
        return False

    def _process_export_special(self):
        # Searching for additional attachments and returns the result in a decoded format
        if self.object._name in ['hr.applicant', 'hr.employee']:
            return self.env['ir.attachment'].search([
                ('res_model', '=', self.object._name), ('res_id', '=', self.object.id)
            ])
        return False

    def _prepare_export_data(self):
        fields = getattr(self, '_personal_fields_%s' % self.object._table)()
        line = []
        for field in fields:
            value = getattr(self.object, field)
            if value and self.object._fields[field].type == 'many2one':
                value = value.name_get()[0][1]
            line.append(value or '')
        return fields, line

    def _export_csv(self, log):
        fields, line = self._prepare_export_data()
        attachments = self._process_export_special() or []
        csv_filename = self.object._table + '_' + re.sub('[^A-Za-z0-9]+', '_', self.object.name_get()[0][1])

        with StringIO() as csv_stream, BytesIO() as zip_stream:
            writer = csv.writer(csv_stream)
            writer.writerow(fields)
            writer.writerow(line)

            with zipfile.ZipFile(zip_stream, 'w') as myzip:
                myzip.writestr(csv_filename + '.csv', csv_stream.getvalue())

                for attachment in attachments:
                    myzip.writestr(attachment.name, base64.b64decode(attachment.datas))
                if 'image' in self.object and self.object.image:
                    myzip.writestr('image', base64.b64decode(self.object.image))

            out = base64.b64encode(zip_stream.getvalue())

        zip_filename = csv_filename + '.zip'
        return self.env['ir.attachment'].sudo().create({
            'type': 'binary',
            'name': zip_filename,
            'store_fname': zip_filename,
            'datas': out,
            'res_model': 'eu.gdpr_log',
            'res_id': log.id,
        }).id
