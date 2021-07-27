odoo.define('one_click_form_edit.form_edit', function(require) {
"use strict";

var FormController = require('web.FormController');

FormController.include({
    _shouldBounceOnClick(element) {
        if (this.mode === 'readonly') {
            this._setMode('edit');
        }
    },
})
return FormController;
});