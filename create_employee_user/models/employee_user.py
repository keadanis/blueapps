# -*- coding: utf-8 -*-

import logging

import werkzeug
from urllib.parse import urljoin
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    user_check_tick = fields.Boolean(default=False)

    @api.onchange('address_home_id')
    def user_checking(self):
        if self.address_home_id:
            self.user_check_tick = True
        else:
            self.user_check_tick = False


class User(models.Model):
    _inherit = ['res.users']

    def action_create_user(self):
        obj_employee_id = self.env['hr.employee'].search([('user_check_tick', '=', False)])
        if obj_employee_id:
            for obj_employee in obj_employee_id:
                if obj_employee.work_email and obj_employee.work_email.find('@') >= 0:
                    obj_user_id = self.env['res.users'].search([('login', '=', obj_employee.work_email)])
                    if not obj_user_id:
                        # portal_id = self.env['res.groups'].search([('is_portal', '=', True)])
                        user_id = self.env['res.users'].create({'name': obj_employee.name, 'login': obj_employee.work_email, 'active': True})
                        if user_id:
                            # if portal_id:
                            #     user_id.groups_id = [(4, portal_id[0].id)]
                            partner = user_id.partner_id
                            obj_employee.address_home_id = partner.id
                            obj_employee.user_id = user_id.id
                            obj_employee.user_check_tick = True
                            partner.signup_prepare()
                            user_id.with_context(active_test=True)._send_email()
                            user_id.refresh()
                            logging.info("User and contact created")
                        else:
                            logging.info("Not user created")
        return False

    def _send_email(self):
        """ send notification email to a new portal user """
        if not self.env.user.email:
            raise UserError(_('You must have an email address in your User Preferences to send emails.'))
        # determine subject and body in the portal user's language
        template = self.env.ref('create_employee_user.mail_template_data_employee_welcome')
        for user in self:
            partner = user.partner_id
            lang = user.lang
            portal_url = partner.with_context(signup_force_type_in_url='', lang=lang)._get_signup_url_for_action()[
                partner.id]
            partner.signup_prepare()
            if template:
                template.with_context(dbname=self._cr.dbname, portal_url=portal_url, lang=lang).send_mail(user.id, force_send=True)
            else:
                logging.warning("No email template found for sending email to the portal user")
        return True

    def _get_signup_url_for_action(self, action=None, view_type=None, menu_id=None, res_id=None, model=None):
        """ generate a signup url for the given partner ids and action, possibly overriding the url state components (menu_id, id, view_type) """
        res = dict.fromkeys(self.ids, False)
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        for partner in self:
            # when required, make sure the partner has a valid signup token
            if self.env.context.get('signup_valid') and not partner.user_ids:
                partner.sudo().signup_prepare()

            route = 'login'
            # the parameters to encode for the query
            query = dict(db=self.env.cr.dbname)
            signup_type = self.env.context.get('signup_force_type_in_url', partner.sudo().signup_type or '')
            if signup_type:
                route = 'reset_password' if signup_type == 'reset' else signup_type

            if partner.sudo().signup_token and signup_type:
                query['token'] = partner.sudo().signup_token
            elif partner.user_ids:
                query['login'] = partner.user_ids[0].login
            else:
                continue  # no signup token, no user, thus no signup url!

            fragment = dict()
            base = '/web#'
            if action == '/mail/view':
                base = '/mail/view?'
            elif action:
                fragment['action'] = action
            if view_type:
                fragment['view_type'] = view_type
            if menu_id:
                fragment['menu_id'] = menu_id
            if model:
                fragment['model'] = model
            if res_id:
                fragment['res_id'] = res_id

            if fragment:
                query['redirect'] = base + werkzeug.url_encode(fragment)

            res[partner.id] = urljoin(base_url, "/web/%s?%s" % (route, werkzeug.url_encode(query)))
        return res
