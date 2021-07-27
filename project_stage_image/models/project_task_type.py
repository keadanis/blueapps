from odoo import fields, models


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    image = fields.Image("Stage Image",
                         max_width=500,
                         max_height=500)
