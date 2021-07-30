odoo.define('nibbana.support', function (require) {
    "use strict";

    var core = require('web.core');
    var AbstractAction = require('web.AbstractAction');

    var Support = AbstractAction.extend({
        template: 'nibbana.support',

        init: function (parent, value) {
            this._super(parent);
        },

    });

    core.action_registry.add('nibbana.support', Support);
});

odoo.define('nibbana.addons', function (require) {
    "use strict";

    var core = require('web.core');
    var AbstractAction = require('web.AbstractAction');

    var Addons = AbstractAction.extend({
        template: 'nibbana.addons',

        init: function (parent, value) {
            this._super(parent);
        },

    });

    core.action_registry.add('nibbana.addons', Addons);
});



