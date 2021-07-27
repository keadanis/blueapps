import json

from odoo import http
from odoo.http import request


class ProjectTaskTypeController(http.Controller):

    @http.route(['/check_project_task_type_image'],
                type='http',
                auth='public',
                methods=['GET'],
                website=True,
                sitemap=False)
    def check_project_task_type_image(self, project_task_type_id=0):
        """
        check if this project task type
        has a photo or not.
        :param project_task_type_id: id of the stage
        :return: bool
        """

        has_image = bool(request.env['project.task.type'].
                         browse(int(project_task_type_id)).image)

        return json.dumps({
            'has_image': has_image,
        }, ensure_ascii=False)
