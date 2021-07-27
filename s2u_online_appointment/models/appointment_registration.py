# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AppointmentRegistration(models.Model):
    _name = 's2u.appointment.registration'
    _description = 'Appointment Registration'
    _inherit = ['portal.mixin', 'mail.thread.cc', 'mail.activity.mixin']

    event_id = fields.Many2one('calendar.event', string='Event', required=True, ondelete='cascade')
    partner_id = fields.Many2one('res.partner', string='Contact', ondelete='cascade')
    appointee_id = fields.Many2one('res.partner', string='Appointee', ondelete='cascade')
    appointment_begin = fields.Datetime(string="Event Start Date", related='event_id.start', readonly=True, store=True)
    appointment_end = fields.Datetime(string="Event End Date", related='event_id.stop', readonly=True)
    name = fields.Char(string='Event', related='event_id.name', readonly=True, store=True)
    state = fields.Selection([
        ('pending', _('Pending')),
        ('valid', _('Scheduled')),
        ('cancel', _('Canceled')),
    ], required=True, default='valid', string='Status', copy=False)
    appointee_interaction = fields.Boolean(string='Appointee interaction', default=False)

    def cancel_appointment(self):
        for appointment in self:
            if appointment.state in ['pending', 'valid']:
                appointment.sudo().event_id.write({
                    'active': False
                })
                appointment.write({
                    'state': 'cancel'
                })

        return True

    def confirm_appointment(self):

        for appointment in self:
            if appointment.state == 'pending':
                appointment.write({
                    'state': 'valid'
                })

        return True
