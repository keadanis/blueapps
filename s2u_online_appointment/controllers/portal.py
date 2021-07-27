# -*- coding: utf-8 -*-

from collections import OrderedDict
from operator import itemgetter

from odoo import http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager


class CustomerPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        values['appointment_count'] = request.env['s2u.appointment.registration'].search_count(['|', ('partner_id', '=', request.env.user.partner_id.id),
                                                                                                     '&', ('appointee_id', '=', request.env.user.partner_id.id),
                                                                                                          ('appointee_interaction', '=', True)])
        return values

    # ------------------------------------------------------------
    # My Appointment
    # ------------------------------------------------------------
    def _appointment_get_page_view_values(self, appointment, access_token, **kwargs):
        values = {
            'page_name': 'appointment',
            'appointment': appointment,
        }
        return self._get_page_view_values(appointment, access_token, values, 'my_appointment_history', False, **kwargs)

    @http.route(['/my/online-appointments', '/my/online-appointments/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_appointments(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw):
        values = self._prepare_portal_layout_values()
        domain = ['|', ('partner_id', '=', request.env.user.partner_id.id),
                       '&', ('appointee_id', '=', request.env.user.partner_id.id),
                            ('appointee_interaction', '=', True)]

        searchbar_sortings = {
            'new': {'label': _('Newest'), 'order': 'id desc'},
            'date1': {'label': _('Date ↓'), 'order': 'appointment_begin'},
            'date2': {'label': _('Date ↑'), 'order': 'appointment_begin desc'},
            'name': {'label': _('Name'), 'order': 'name'},
        }
        if not sortby or sortby not in searchbar_sortings.keys():
            sortby = 'new'
        order = searchbar_sortings[sortby]['order']

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'pending': {'label': _('Pending'), 'domain': [('state', '=', 'pending')]},
            'valid': {'label': _('Confirmed'), 'domain': [('state', '=', 'valid')]},
            'cancel': {'label': _('Canceled'), 'domain': [('state', '=', 'cancel')]},
        }
        if not filterby:
            filterby = 'all'
        domain = searchbar_filters[filterby]['domain'] + domain

        if date_begin and date_end:
            domain = [('create_date', '>', date_begin), ('create_date', '<=', date_end)] + domain
        # appointments count
        appointment_count = request.env['s2u.appointment.registration'].search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/online-appointments",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=appointment_count,
            page=page,
            step=self._items_per_page
        )

        # content according to pager and archive selected
        appointments = request.env['s2u.appointment.registration'].search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_appointments_history'] = appointments.ids[:100]

        values.update({
            'date': date_begin,
            'date_end': date_end,
            'appointments': appointments,
            'page_name': 'appointment',
            'default_url': '/my/online-appointments',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
        })
        return request.render("s2u_online_appointment.portal_my_appointments", values)

    @http.route(['/my/online-appointment/<int:appointment_id>'], type='http', auth="public", website=True)
    def portal_my_appointment(self, appointment_id=None, access_token=None, **kw):
        try:
            appointment_sudo = self._document_check_access('s2u.appointment.registration', appointment_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        values = self._appointment_get_page_view_values(appointment_sudo, access_token, **kw)
        return request.render("s2u_online_appointment.portal_my_appointment", values)
