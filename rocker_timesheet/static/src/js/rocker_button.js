odoo.define('rocker_timesheet.button', function(require) {
    'use strict';

    var core = require('web.core');
    var CalendarPopover = require('web.CalendarPopover');
    var CalendarController = require("web.CalendarController");
    var CalendarRenderer = require("web.CalendarRenderer");
    var CalendarView = require("web.CalendarView");
    var viewRegistry = require('web.view_registry');
    var ListController = require('web.ListController');
    var ListView = require("web.ListView");

    var _t = core._t;
    var QWeb = core.qweb;


    var RockerCalendarController = CalendarController.extend({
        events: _.extend({}, CalendarController.prototype.events, {
            'click .btn-all': '_onAll',
            'click .btn-billable': '_onBillable',
            'click .btn-nonbillable': '_onNonBillable',
            'click .btn-internal': '_onInternal',
            'click .btn-member': '_onMember',
            'click .btn-mine': '_onMine',
        }),

        start: function () {
            this.$el.addClass('o_rocker_calendar');
            return this._super(...arguments);
        },

         //--------------------------------------------------
         // Buttons
         //--------------------------------------------------

        renderButtons: function ($node) {
            this._super.apply(this, arguments);
            $(QWeb.render('rocker_timesheet.button', {
                all: _t('All'),
                billable: _t('Billable'),
                nonbillable: _t('NonBillable'),
                internal: _t('Internal'),
                member: _t('Member'),
                mine: _t('My'),
            })).appendTo(this.$buttons);

            this.$buttons.appendTo($node);
//            if ($node) {
//                this.$buttons.appendTo($node);
//            } else {
//                this.$('.o_calendar_buttons').replaceWith(this.$buttons);
//            }
        },

        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------

        _onAll: function () {
            var self = this;
            this.do_action('rocker_timesheet.action_searchpanel_all_tasks', {
                on_close: function () {
                    self.reload();
                }
            });
        },
        _onMember: function () {
            var self = this;
            this.do_action('rocker_timesheet.action_searchpanel_member_tasks', {
                on_close: function () {
                    self.reload();
                }
            });
        },
        _onBillable: function () {
            var self = this;
            this.do_action('rocker_timesheet.action_searchpanel_billable_tasks', {
                on_close: function () {
                    self.reload();
                }
            });
        },
        _onNonBillable: function () {
            var self = this;
            this.do_action('rocker_timesheet.action_searchpanel_nonbillable_tasks', {
                on_close: function () {
                    self.reload();
                }
            });
        },
        _onInternal: function () {
            var self = this;
            this.do_action('rocker_timesheet.action_searchpanel_internal_tasks', {
                on_close: function () {
                    self.reload();
                }
            });
        },
        _onMine: function () {
            var self = this;
            this.do_action('rocker_timesheet.action_searchpanel_mine_tasks', {
                on_close: function () {
                    self.reload();
                }
            });
        },
    });

    var RockerCalendarView = CalendarView.extend({
        config: _.extend({}, CalendarView.prototype.config, {
            Controller: RockerCalendarController,
        }),
    });

    viewRegistry.add('rocker_calendar', RockerCalendarView);

    var RockerListController = ListController.extend({
        events: _.extend({}, ListController.prototype.events, {
            'click .btn-all': '_onAll',
            'click .btn-billable': '_onBillable',
            'click .btn-nonbillable': '_onNonBillable',
            'click .btn-internal': '_onInternal',
            'click .btn-member': '_onMember',
            'click .btn-mine': '_onMine',
        }),
        start: function () {
            this.$el.addClass('o_rocker_tree');
            return this._super(...arguments);
        },

         //--------------------------------------------------
         // Buttons
         //--------------------------------------------------

        renderButtons: function ($node) {
            this._super.apply(this, arguments);
            $(QWeb.render('rocker_timesheet.button', {
                all: _t('All'),
                billable: _t('Billable'),
                nonbillable: _t('NonBillable'),
                internal: _t('Internal'),
                member: _t('Member'),
                mine: _t('My'),
            })).appendTo(this.$buttons);

            this.$buttons.appendTo($node);
        },

        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------

        _onAll: function () {
            var self = this;
            this.do_action('rocker_timesheet.action_searchpanel_all_tasks', {
                on_close: function () {
                    self.reload();
                }
            });
        },
        _onMember: function () {
            var self = this;
            this.do_action('rocker_timesheet.action_searchpanel_member_tasks', {
                on_close: function () {
                    self.reload();
                }
            });
        },
        _onBillable: function () {
            var self = this;
            this.do_action('rocker_timesheet.action_searchpanel_billable_tasks', {
                on_close: function () {
                    self.reload();
                }
            });
        },
        _onNonBillable: function () {
            var self = this;
            this.do_action('rocker_timesheet.action_searchpanel_nonbillable_tasks', {
                on_close: function () {
                    self.reload();
                }
            });
        },
        _onInternal: function () {
            var self = this;
            this.do_action('rocker_timesheet.action_searchpanel_internal_tasks', {
                on_close: function () {
                    self.reload();
                }
            });
        },
        _onMine: function () {
            var self = this;
            this.do_action('rocker_timesheet.action_searchpanel_mine_tasks', {
                on_close: function () {
                    self.reload();
                }
            });
        },
    });

    var RockerListView = ListView.extend({
        config: _.extend({}, ListView.prototype.config, {
            Controller: RockerListController,
        }),
    });


    viewRegistry.add('rocker_tree', RockerListView);


});
