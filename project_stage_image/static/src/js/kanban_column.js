odoo.define('project_stage_image.KanbanColumn', function (require) {
    "use strict"

    var session = require('web.session');
    var KanbanColumn = require('web.KanbanColumn');

    KanbanColumn.include({
        /**
        * @override
        * add the column image to the
        * top of the column
        */
        start: function () {

            var self = this;

            // make sure that the stage
            // is not folded
            if ((!this.folded) && (this.modelName == 'project.task')) {

                // current url, <domain_name>:<port_number>
                var url = window.location.origin;

                // get the id of the stage
                var projectTaskTypeId = self.id

                // use ajax to check if the stage has an image.
                // if there is no image, remove the anchor, else
                // use the stage's image as the img src
                $.ajax({
                    type: 'GET',
                    data: {'project_task_type_id': projectTaskTypeId},
                    url: `${url}/check_project_task_type_image`,
                    success: function (result) {
                        var result = JSON.parse(result);
                        if (result.has_image == true) {

                            // construct the img source.
                            // it should point at the image
                            // field of task stage record
                            var src = `${url}/web/image?model=project.task.type&id=${projectTaskTypeId}&field=image`;

                            // create the image and give it
                            // the correct source
                            var img = $(`<img id='stage-image-${projectTaskTypeId}' alt=${projectTaskTypeId} src=${src} height="120" width="240">`);

                            // append the image into the template
                            $(`[data-id=${projectTaskTypeId}]`)[0].firstElementChild.append(img[0])
                        }
                    },
                    error: function (xhr, ajaxOptions, thrownError) {
                        console.log('Error encountered');
                    },
                });
            }
            // return super
            return this._super.apply(this, arguments);
        }
    })
});