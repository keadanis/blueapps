

odoo.define('nutikad_theme.settingsicon', function (require){
"use strict";
// require original module JS
var BaseSetting = require('base.settings');
BaseSetting.Renderer.include({
    _getAppIconUrl: function (module) {
        return module = "/"+'nutikad_theme'+"/static/general_settings_icon/"+module+".png";
    }
});
});
