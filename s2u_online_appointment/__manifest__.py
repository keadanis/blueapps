# -*- coding: utf-8 -*-

{
    'name': 'Online appointment',
    'version': '14.0.1.2',
    'author': 'Solutions2use',
    'price': 0.0,
    'currency': 'EUR',
    'maintainer': 'Solutions2use',
    'support': 'info@solutions2use.com',
    'images': ['static/description/app_logo.jpg'],
    'license': 'OPL-1',
    'website': 'https://www.solutions2use.com',
    'category':  'Website',
    'summary': 'Let visitors book an appointment over the website',
    'description':
        """Visitors can book appointments over the website. A calendar pops up, the days marked green are available for selection.
        After selecting a date the visitor needs to choose a timeslot and a appointment option. In the backend you define per
        user his available timeslots. Only timeslots are selectable by the visitor when no other "calendar.event" is present for that period of time.
        Appointment options you define globally in the backend and have a duration. This way a "calendar.event" is created with the correct start and stop.
        
        website appointment
        online appointment
        portal appointment
        appointment
        website meeting
        online meeting
        portal meeting
        meeting
         
        """,
    'depends': [
        'calendar',
        'website',
        'portal'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/appointment_template.xml',
        'views/appointment_portal_template.xml',
        'views/menus.xml',
        'views/appointment_slot_view.xml',
        'views/appointment_option_view.xml',
    ],
    'qweb': [
    ],
    'installable': True,
    'auto_install': False,
}

