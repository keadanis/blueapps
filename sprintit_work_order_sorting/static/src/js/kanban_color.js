odoo.define('sprintit_work_order_sorting.kanban_color', function (require) {
"use strict";

/**
 * This file defines the Color for the Kanban view of MRP Work Order.
 */
var KanbanRecord = require('web.KanbanRecord');
	
KanbanRecord.include({
				_render : function() {
					var self = this;
					var WorkOrderRecord = this._super.apply(this, arguments);
					if (this.modelName === 'mrp.workorder'
							&& this.record.kanban_color) {
						this.$el.css("background-color",
								this.record.kanban_color.value);
					}
					return WorkOrderRecord
				}
			});
});
