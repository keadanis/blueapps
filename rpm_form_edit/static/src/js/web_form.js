odoo.define('rpm_form_edit.EditableListRenderers', function (require) {
"use strict";

var core = require('web.core');
var dom = require('web.dom');
var List = require('web.ListRenderer');
var utils = require('web.utils');

var _t = core._t;

List.include({
    _onRowClicked: function (event) {
        if (!$(event.target).prop('special_click')) {
            var id = $(event.currentTarget).data('id');
            if (id) {
                this.trigger_up('open_record', { id: id, target: event.target, mode: 'edit'});
            }
        }
    },
});

});