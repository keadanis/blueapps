odoo.define('aspl_float_speedometer.widget', function(require) {
    "use strict";
    var core = require('web.core');
    var widget = require('web.basic_fields');
    var fieldRegistry = require('web.field_registry');
    var FieldSpeed = widget.FieldFloat.extend({
        template : 'FieldSpeed',
        _getValue : function() {
           return this.$('input').val();
          },
          _render : function() {
                  var $this = this
                  var value = this.value
                  var height = $this.$('input')[0].style.height
                  var width = $this.$('input')[0].style.width
                  var maxvalue = parseInt($this.$('input')[0].max)
                  this.$('.o_form_input').hide();
                  this.$('#oe_radio_gauge').css('display','block;');
                  this.$('#oe_radio_gauge').css('margin-top','-33px !important');
                  this.$('#oe_radio_gauge').css('margin-left','-35px !important');
                  this.$("#radialgauge").igRadialGauge({

                        maximumValue: maxvalue,
                        value: value,
                        isNeedleDraggingEnabled: true,
                        backingStrokeThickness: "1",
                        backingOutline:"#7c7bad",
                        fontBrush:"black",
                        tickBrush: "gray",
                        minorTickBrush: "#7c7bad",
                        scaleStartAngle: "180",
                        scaleEndAngle: "0",
                        scaleBrush: "transparent",
                        needleShape: "needle",
                        needlePivotShape: "circleOverlay",
                        needleEndExtent: "0.55",
                        needlePointFeatureExtent: "0.3",
                        needlePivotWidthRatio: "0.2",
                        backingShape: "fitted",
                        valueChanged: function(evt, ui) {
                            if (!$this.$silent) {
                                 if ($this.mode === 'edit' && $this.$('input').val() !== '') {
                                     $this._setValue($this._getValue());
                                     $this.$('input').val(ui.newValue)
                                 }
                            }
                        }
                    });
                  if (this.mode === 'edit'){
                    this.$("#radialgauge").igRadialGauge("option", "isNeedleDraggingEnabled", true)

                  }
                  else{
                    this.$("#radialgauge").igRadialGauge("option", "isNeedleDraggingEnabled", false)
                  }
                  if (height && width){
                    this.$('#oe_radio_gauge').css('height',String(height))
                    this.$('#oe_radio_gauge').css('width',String(width))
                    this.$("#radialgauge").igRadialGauge("option", "height", height)
                    this.$("#radialgauge").igRadialGauge("option", "width", width)
                  }
                  else{
                    this.$("#radialgauge").igRadialGauge("option", "height", '250px')
                    this.$("#radialgauge").igRadialGauge("option", "width", '90%')
                  }
                this.$('input').val(this.value)
          },
          _onInput: function(){
            this.$input = this.$('input');
            this._super();
            }
    });
    fieldRegistry.add('speedometer', FieldSpeed);
    return {
       FieldSpeed : FieldSpeed
    };
});
