odoo.define('akl_theme_base.AppsMenu', function (require) {
    "use strict";

    var Widget = require('web.Widget');
    var aklBus = require('akl_theme_base.bus')
    var core = require('web.core')
    var qweb = core.qweb

    var aklAppsMenu = Widget.extend({
        template: 'akl_theme_base.app_menu',

        events: _.extend({}, Widget.prototype.events, {
            "click .akl_app_item": "_on_app_item_click"
        }),

        init: function (parent, menuData) {
            this._super.apply(this, arguments);

            this.$menu_sections = {};
            this.menu_data = menuData;

            this._apps = _.map(menuData.children, function (appMenuData) {
                return {
                    actionID: parseInt(appMenuData.action.split(',')[1]),
                    menuID: appMenuData.id,
                    name: appMenuData.name,
                    xmlID: appMenuData.xmlid,
                    web_icon_data: appMenuData.web_icon_data
                };
            });
        },

        start: function () {
            this._super.apply(this, arguments)
            aklBus.on('akl_active_app_item', this, this._active_app)
        },

        getApps: function () {
            return this._apps;
        },

        /**
         * active the app item
         * @param {} action_id 
         */
        _active_app: function (event) {
            var data = event.data
            this.$('.akl_app_item > a').removeClass('active')
            var app_item = this.$('a[data-menu-id=' + data.menu_id + ']')
            app_item.addClass('active')
        },

        _get_app_data: function (menu_id) {
            var app = undefined
            for (var i = 0; i < this.menu_data.children.length; i++) {
                if (this.menu_data.children[i].id == menu_id) {
                    app = this.menu_data.children[i]
                    break;
                }
            }
            return app
        },

        _trigger_menu_clicked: function (menu_id, action_id) {
            this.trigger_up('menu_clicked', {
                id: menu_id,
                action_id: action_id
            });
        },

        _isMenuExsits: function (menuID) {
            return _.find(this._apps, function (tmpApp) {
                return tmpApp.menuID == menuID
            })
        },

        _on_app_item_click: function (event) {
            var $target = $(event.currentTarget)
            var action_id = $target.data('action-id')
            aklBus.trigger('akl_app_name_clicked', action_id);
        }
    });

    return aklAppsMenu;
});
