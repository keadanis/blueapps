odoo.define('nutikad_theme.UserMenu', function (require){
"use strict";
// require original module JS
var menu = require('web.UserMenu');

var config = require('web.config');
var core = require('web.core');
var framework = require('web.framework');
var Dialog = require('web.Dialog');
var Widget = require('web.Widget');

var _t = core._t;
var QWeb = core.qweb;

menu.include({
    /**
     * @override
     */
    init: function () {
        this._super.apply(this, arguments);
    },
    _onMenuCalendar: function () {
        var self = this;
        var session = this.getSession();
        
        this.trigger_up('clear_uncommitted_changes', {
            callback: function () {
                self._rpc({
                        model: "user.menu",
                        method: "calendar_action_get"
                    })
                    .then(function (result) {
                        result.res_id = session.uid;
                        self.do_action(result);
                    });
            },
        });
    },
    _onMenuContact: function () {
        var self = this;
        var session = this.getSession();
        this.trigger_up('clear_uncommitted_changes', {
            callback: function () {
                self._rpc({
                        model: "user.menu",
                        method: "contact_action_get"
                    })
                    .then(function (result) {
                        result.res_id = session.uid;
                        self.do_action(result);
                    });
            },
        });
    },
    _onMenuDiscuss: function () {
        var self = this;
        var session = this.getSession();
        this.trigger_up('clear_uncommitted_changes', {
            callback: function () {
                self._rpc({
                        model: "user.menu",
                        method: "discuss_action_get"
                    })
                    .then(function (result) {
                        result.res_id = session.uid;
                        self.do_action(result);
                    });
            },
        });
    },

    _onMenuAttendance: function () {
        var self = this;
        var session = this.getSession();
        this.trigger_up('clear_uncommitted_changes', {
            callback: function () {
                self._rpc({
                        model: "user.menu",
                        method: "attendance_action_get"
                    })
                    .then(function (result) {
                        result.res_id = session.uid;
                        self.do_action(result);
                    });
            },
        });
    },
});
});