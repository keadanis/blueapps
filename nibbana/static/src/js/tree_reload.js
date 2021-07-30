odoo.define("nibbana.tree_reload", function (require) {
    "use strict";
  
    var WebClient = require('web.WebClient');
    var channel = 'nibbana_tree_reload';

    WebClient.include({
        start: function(){
            this._super()
            this.call('bus_service', 'addChannel', channel);
            this.call('bus_service', 'onNotification', this,
                      this.on_nibbana_tree_notification)
        },

        on_nibbana_tree_notification: function (notification) {
          for (var i = 0; i < notification.length; i++) {
             var ch = notification[i][0]
             var msg = notification[i][1]
             if (ch == channel) {
                 try {
                  this.nibbana_tree_handle_message(msg)
                }
                catch(err) {console.log(err)}
             }
           }
        },

        nibbana_tree_handle_message: function(msg) {
          var action = this.action_manager && this.action_manager.getCurrentAction()
          if (!action) {
              //console.log('Action not loaded')
              return
          }
          var controller = this.action_manager.getCurrentController()
          if (!controller) {
              //console.log('Controller not loaded')
              return
          }          
          if (!controller.widget.modelName.includes("nibbana.")) {
            //console.log('Not Nibbana Active Calls view')
            return
          }
          if (msg == 'reload') {
            //console.log('Reload')
            controller.widget.reload()
          }
        },
    })
})
