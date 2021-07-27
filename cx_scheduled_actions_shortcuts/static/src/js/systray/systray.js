/**********************************************************************************
* 
*    Copyright (C) 2020 Cetmix OÜ
*
*    This program is free software: you can redistribute it and/or modify
*    it under the terms of the GNU LESSER GENERAL PUBLIC LICENSE as
*    published by the Free Software Foundation, either version 3 of the
*    License, or (at your option) any later version.
*
*    This program is distributed in the hope that it will be useful,
*    but WITHOUT ANY WARRANTY; without even the implied warranty of
*    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
*    GNU LESSER GENERAL PUBLIC LICENSE for more details.
*
*    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
*    along with this program.  If not, see <http://www.gnu.org/licenses/>.
*
**********************************************************************************/

odoo.define("cx_scheduled_act.systray", function(require) {
  "use strict";

  var core = require("web.core");
  var _t = core._t;
  var SystrayMenu = require("web.SystrayMenu");
  var Widget = require("web.Widget");

  var QWeb = core.qweb;

  /**
   * Menu item appended in the systray part of the navbar
   *
   **/
  var CxScheduledActMenu = Widget.extend({
    template: "cx_scheduled_act.CxScheduledActMenu",
    events: {
      "click .o_cx_schedule_act_preview": "_onCxScheduleActPreviewClick",
      "click .o_cx_schedule_settings": "_onCxScheduleActSettingsClick",
      "show.bs.dropdown": "_onCxScheduledActMenuClick",
    },
    init: function() {
      this._super.apply(this, arguments);
    },
    start: function() {
      this.$cx_schedule_act_preview = this.$(
        ".o_cx_schedule_act_navbar_dropdown_items"
      );

      return this._super();
    },
    // --------------------------------------------------
    // Private
    // --------------------------------------------------
    /**
     * Make RPC and get ir.cron details
     * @private
     */
    _getCxScheduledActData: function() {
      var self = this;

      return self
        ._rpc({
          model: "ir.cron",
          method: "get_shortcuts",
        })
        .then(function(data) {
          self.crons = data;
        });
    },
    /**
     * Check wether cx_sched systray dropdown is open or not
     * @private
     * @returns {Boolean}
     */
    _isOpen: function() {
      return this.$el.hasClass("open");
    },
    /**
     * Update(render) cx_sched system tray view on cx_sched updation.
     * @private
     */
    _updateCxScheduledActPreview: function() {
      var self = this;
      self._getCxScheduledActData().then(function() {
        self.$cx_schedule_act_preview.html(
          QWeb.render("cx_scheduled_act.CxScheduledActMenuPreview", {
            crons: self.crons,
          })
        );
      });
    },
    /**
     * When menu clicked update cx_sched preview
     * @private
     * @param {MouseEvent} event
     */
    _onCxScheduledActMenuClick: function() {
      if (!this._isOpen()) {
        this._updateCxScheduledActPreview();
      }
    },
    _onCxScheduleActPreviewClick: function($event) {
      var self = this;
      const cronId = $($event.target).attr("cron_id");

      return self
        ._rpc({
          model: "ir.cron",
          method: "run_shortcut_action",
          args: [[parseInt(cronId)]],
        })
        .then(function(data) {
          self.resPrev = data;
        });
    },
    _onCxScheduleActSettingsClick: function() {
      const action = {
        name: _t("Scheduled Actions"),
        type: "ir.actions.act_window",
        res_model: "ir.cron",
        views: [
          [false, "list"],
          [false, "form"],
        ],
        target: "current",
      };
      var self = this;
      self.do_action(action, {
        on_close: self.trigger_up.bind(self, "reload"),
      });
    },
  });

  SystrayMenu.Items.push(CxScheduledActMenu);
  return CxScheduledActMenu;
});
