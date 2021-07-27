odoo.define('rpm_form_edit.KanbanRecordInherit', function(require) {
"use strict";

var Kanban = require('web.KanbanRecord');

Kanban.include({
    _openRecord: function () {
        if (this.$el.hasClass('o_currently_dragged')) {
            return;
        }
        var editMode = this.$el.hasClass('oe_kanban_global_click_edit');
        this.trigger_up('open_record', {
            id: this.db_id,
            mode: 'edit',
        });
    },
});
});