odoo.define('my_color_company.ResConfigEdition', function (require) {
    "use strict";

    var Widget = require('web.Widget');
    var widget_registry = require('web.widget_registry');
    var session = require ('web.session');
    var rpc = require('web.rpc');

    var ResConfigEdition = Widget.extend({
        template: 'res_config_edition',

       /**
        * @override
        */
        init: function () {
            this._super.apply(this, arguments);
            this.server_version = session.server_version;            
            this.test = session;
            console.log(session['user_companies']['allowed_companies']);
            console.log(session);
           
        },
   });

   widget_registry.add('res_config_edition', ResConfigEdition);

    return ResConfigEdition;
});
