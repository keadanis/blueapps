# Copyright 2018, 2021 Heliconia Solutions Pvt Ltd (https://heliconia.io)

from datetime import datetime, timedelta

from odoo import api, fields, models
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model
    def get_employee_birthday_info(self):
        reminder_before_day = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("employee.reminder_before_day")
        )
        next_date = datetime.today() + timedelta(days=int(reminder_before_day or 1))
        employee_ids = self.env["hr.employee"].search(
            [
                ("birthday_date", "=", next_date.day),
                ("birthday_month", "=", next_date.month),
            ]
        )
        return {
            "employees": employee_ids,
            "date": next_date.strftime(DEFAULT_SERVER_DATE_FORMAT),
        }


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    birthday_date = fields.Integer(compute="_compute_get_birthday_identifier", store=1)
    birthday_month = fields.Integer(compute="_compute_get_birthday_identifier", store=1)

    @api.depends("birthday")
    def _compute_get_birthday_identifier(self):
        for employee in self.filtered(lambda e: e.birthday):
            employee.birthday_date = employee.birthday.day
            employee.birthday_month = employee.birthday.month

    @api.model
    def send_birthday_reminder_employee(self):
        IrConfigParameter = self.env["ir.config_parameter"].sudo()
        template_env = self.env["mail.template"]
        send_employee = bool(IrConfigParameter.get_param("employee.send_wish_employee"))
        send_manager = bool(IrConfigParameter.get_param("employee.send_wish_manager"))

        # Send birthday wish to employee
        if send_employee:
            domain = [
                ("birthday_date", "=", datetime.today().day),
                ("birthday_month", "=", datetime.today().month),
            ]
            emp_template_id = IrConfigParameter.get_param(
                "employee.emp_wish_template_id"
            )
            if emp_template_id:
                template_id = template_env.sudo().browse(int(emp_template_id))
                for employee in self.env["hr.employee"].search(domain):
                    template_id.send_mail(employee.id)

        # Send birthday reminder to HR manager
        if send_manager:
            birthday_info = self.env["res.users"].get_employee_birthday_info()
            if len(birthday_info.get("employees")):
                manager_template_id = IrConfigParameter.get_param(
                    "employee.manager_wish_template_id"
                )
                if manager_template_id:
                    template_id = template_env.sudo().browse(int(manager_template_id))
                    for manager in self.env.ref("hr.group_hr_manager").users:
                        template_id.send_mail(manager.id)
