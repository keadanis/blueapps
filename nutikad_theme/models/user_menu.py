from odoo import api, fields, models, tools


class UserMenu(models.Model):
    _name = "user.menu"

    @api.model
    def calendar_action_get(self):
        return self.sudo().env.ref('calendar.action_calendar_event').read()[0]

    @api.model
    def contact_action_get(self):
        return self.sudo().env.ref('contacts.action_contacts').read()[0]

    @api.model
    def discuss_action_get(self):
        return self.sudo().env.ref('mail.action_discuss').read()[0]

    @api.model
    def attendance_action_get(self):
        return self.sudo().env.ref('hr_attendance.hr_attendance_action_my_attendances').read()[0]
