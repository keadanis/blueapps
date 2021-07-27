# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Create Task from Lead',
    'version': '14.0.0.0',
    'category': 'CRM',
    'description': """
    Task on Lead, Add Task from lead, Task Lead, Create Project Task from Lead, Add task from mail, Create task from mail.Task on lead, add task on lead, tasks on lead, lead tasks, automated task by lead, Generate task from lead.
""",
    'author': 'BrowseInfo',
    'website': 'https://www.browseinfo.in',
    'images': [],
    'depends': ['base', 'crm', 'sale', 'project'],
    
    'data': [ 'security/ir.model.access.csv',
             'views/crm_lead_view.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    "images":['static/description/Banner.png'],
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
