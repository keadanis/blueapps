import io
import xlwt

from datetime import datetime, timedelta, date
import base64
from odoo.exceptions import ValidationError
from odoo import fields, models, api, _

    
class OdooDynamicReportingLine(models.Model):
    _name = "dynamic.report.line"

    line_id = fields.Many2one('odoo.dynamic.report', required=False)
    field_id = fields.Many2one('ir.model.fields', readonly=False, 
    store=True, required=True) 
    label = fields.Char(string='Export Label', size=10, required=True)
    model_id = fields.Many2one('ir.model', string="Model", required=True)

    @api.onchange('model_id')
    def domain_fields(self):
        if self.model_id:
            model = self.env['ir.model'].browse([self.model_id.id])
            # TODO Will still add more features to on2many report option
            field_ids = [rec.id for rec in model.mapped('field_id').\
                filtered(lambda s: s.ttype not in ["one2many", "many2many"] and s.store == True)] 
            res = [0] if not field_ids else field_ids
            if field_ids:
                domain = {'field_id': [('id', '=', res)]}
                return {'domain': domain}
        else:
            return {'domain': {'field_id': [('id', '=', False)]}}


class OdooDynamicReporting(models.Model):
    _name = "odoo.dynamic.report"

    name = fields.Char(string='Header Name', size=30, required=True)
    excel_file = fields.Binary('Download Excel file', filename='filename',
     readonly=True)
    filename = fields.Char('Excel File', size=64)
    filter_type = fields.Selection([
        ('none','None'),
        ('write_date_range', 'Write Date Range'),
        ('create_date_range', 'Create Date Range')], 
        string='Filter type', default='none')
    model_id = fields.Many2one('ir.model', string="Model", 
    required=True)
    model_fields = fields.One2many('dynamic.report.line', 
    'line_id', string="Field Setup Line")
    start_date = fields.Date('Date To')
    end_date = fields.Date('Date From')

    @api.onchange('model_id')
    def clear_lines(self):
        self.model_fields = False 

    def report_data(self):
        domain, rec_list =[], []
        if self.filter_type == "write_date_range": 
            domain = [
                ('create_date', '>=', self.start_date),
                ('create_date', '<=', self.end_date)
                ]
        elif self.filter_type == "create_date_range":
            domain = [
                ('write_date', '>=', self.start_date),
                ('write_date', '<=', self.end_date)
                ]
        model_name = self.model_id.model
        record_ids = self.env[model_name].search(domain)
        if record_ids:
            for rec in record_ids:
                rec_list = rec
            return rec_list 

    def export_data(self):
        record_Ids = self.report_data()
        header_name = self.name
        model_name = self.model_id.model
        headers = []
        # headers= {
        # 'label': 'Address', 
        # 'field_name', 'My_field'
        # }
        for hd in self.model_fields: 
            dicts = {}
            dicts['label'] = hd.label
            dicts['fieldname'] = hd.field_id.name 
            headers.append(dicts)

        style0 = xlwt.easyxf('font: name Times New Roman, \
            color-index red, bold on', num_format_str='#,##0.00')
        style1 = xlwt.easyxf(num_format_str='DD-MMM-YYYY')
        wb = xlwt.Workbook()
        ws = wb.add_sheet(header_name.title())
        colh = 0
        if record_Ids:
            ws.write(0, 6, ' %s - %s' %(header_name.capitalize() \
                if header_name else '', fields.Date.today()), style0)
            for head in headers:
                ws.write(1, colh, head.get('label'))
                colh += 1
            row = 3
            model_env = self.env[model_name]
            for recs in record_Ids:
                records = model_env.browse([recs.id])
                col = 0
                for dic in headers:
                    try:
                        value = recs[str(dic.get('fieldname'))]
                        type_field = type(value)
                            # TODO: aDD OTHER FIELD TYPE THAT IS NOT SUBSCRIPTABLE
                        if type_field in [str, int, float, bool]:
 
                            result = value 
                        elif type_field in [datetime, date]:
                            result = datetime.strftime(value, '%m/%d/%Y %H:%M:%S')
                        else:
                            ValidationError(value)
                            result = value['name']
                        ws.write(row, col,result) 
                    except Exception as e:
                        raise ValidationError("The following Error Occured \n {}".format(e))
                    col += 1
                row += 1
            fp = io.BytesIO()
            wb.save(fp)
            filename = "{}.xls".format(header_name.title())
            self.excel_file = base64.encodestring(fp.getvalue())
            self.filename = filename
            fp.close()
            
            view = self.env.ref('odoo_dynamic_export.view_odoo_dynamic_report_form')
            view_id = view and view.id or False
            context = dict(self._context or {})
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'odoo.dynamic.report',
                'name': _('Export'),
                'res_id': self.id,
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': view_id,
                'target': 'new',
                'nodestroy': True,
                'context': context
                    }
        else:
            raise ValidationError('No Records found to Export')
    