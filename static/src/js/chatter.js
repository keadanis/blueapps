odoo.define('budget_expense_management.Chatter', function (require) {
"use strict";

var chatter = require('mail.Chatter');
var core = require('web.core');
var _t = core._t;
var QWeb = core.qweb;
var config = require('web.config');


 chatter.include({
    
  start: function () {
  	this._$topbar = this.$('.o_chatter_topbar');
        if(!this._disableAttachmentBox) {
            this.$('.o_topbar_right_area').append(QWeb.render('mail.chatter.Attachment.Button', {
            	displayCounter: !!this.fields.thread,
                count: this.record.data.message_attachment_count || 0,
                cu_model:this.record.model
            }));
        }
        
        return this._super.apply(this, arguments);
  
    },
    
    _renderButtons: function () {
    	this._super.apply(this, arguments);
        return QWeb.render('mail.chatter.Buttons', {
            newMessageButton: !!this.fields.thread,
            logNoteButton: this.hasLogButton,
            scheduleActivityButton: !!this.fields.activity,
            isMobile: config.device.isMobile,
            cu_model:this.record.model
        });
    },
 });
 
 
 
});