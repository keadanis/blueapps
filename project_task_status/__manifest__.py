# -*- coding: utf-8 -*-
# copyright (C) 2020-TODAY Vacker360 Pvt. Ltd (https://www.vacker360.com)
# See LICENSE file for full copyright and licensing details.
{
    'name': "Project Task Status",

    'summary': """
        This module is used to change the color of the task in tree view and kanban view.""",

    'description': """
        project_task_status adds feature to distinguish the task status according to their completion date. It shows unique status for each type of the task finished according their deadline.
    """,

    'author': "Vacker360",
    'website': "https://www.vacker360.com",

    'category': 'Project',
    'version': '0.1',
    'installable': True,
    'license': 'AGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['project_stage_state'],

    # always loaded
    'data': [
        'views/views.xml',
    ],
    'images': [
        'static/description/cover_image.gif',
    ]
}
