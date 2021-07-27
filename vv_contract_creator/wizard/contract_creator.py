from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_TIME_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.safe_eval import _BUILTINS, safe_eval
import calendar
import datetime
import random
import re
import time
import dateutil
import logging

_logger = logging.getLogger(__name__)


class ContractCreator(models.TransientModel):
    _name = 'vv.contract.creator'
    _description = 'Contract Creator'

    contract_template_id = fields.Many2one('vv.contract.template', string='Contract Template', readonly=1)
    contract_creator_line_ids = fields.One2many('contract.creator.line', 'creator_id')

    def create_contract(self):
        self.ensure_one()
        return self.env.ref('vv_contract_creator.action_report_contract').report_action(self.id)

    def _prepare_contract(self):
        self.ensure_one()
        template = self.contract_template_id.template
        for line in self.contract_creator_line_ids:
            if line.keyword_type == 'mapping':
                value_mapped = line.get_mapping_values()
                template = template.replace(line.keyword, value_mapped)
            elif line.keyword_type == 'exec':
                if "result" not in line.value:
                    msg = _("Error while mapping the keyword '{0}': "
                            "The result should be returned inside a 'result' variable."
                            "For example: result = record_id").format(self.keyword)
                    raise ValidationError(msg)
                try:
                    locals_dict = line.exec_python_code()
                    value_mapped = locals_dict['result']
                except Exception:
                    raise UserError(_("Error for keyword {} when running Python mapping *{}*").format(
                        self.keyword, self.value))
                template = template.replace(line.keyword, value_mapped)
        return template


class ContractCreatorLine(models.TransientModel):
    _name = 'contract.creator.line'
    _description = 'Contract Creator Line'

    creator_id = fields.Many2one('vv.contract.creator')
    keyword = fields.Char('Keyword')
    keyword_type = fields.Selection(selection=[
        ('mapping', 'Get field value'),
        ('exec', 'Python Code Execution'),
    ], string='Keyword Type')
    odoo_record_ref = fields.Reference(string='Record Reference', selection='_selection_target_model')
    value = fields.Char('Value to Replace With')

    @api.model
    def _selection_target_model(self):
        return [(model.model, model.name) for model in self.env['ir.model'].search([])]

    def get_mapping_values(self):
        self.ensure_one()
        try:
            values = self.odoo_record_ref.mapped(self.value)
        except KeyError as e:
            msg = (_("Error while mapping the keyword '{0}': "
                     "The field '{1}' used to retrieve the information does not exist in Odoo."
                     "Please, create it, or use another one, Exception : {2}")).format(
                self.keyword, str(self.value), str(e))
            raise ValidationError(msg)
        if not values or (isinstance(values, list) and not values[0]):
            return ''
        else:
            if isinstance(values, models.BaseModel):
                values = self.odoo_record_ref.mapped(self.value + '.display_name')
            if len(values) > 1:
                value_converted = ', '.join(values)
            else:
                value_converted = values[0]
        if not value_converted:
            values_splitted = self.value.split('.')
            len_values_splitted = len(values_splitted)
            rec = self.odoo_record_ref
            i = 0
            while i < len_values_splitted - 1:
                rec = rec.mapped(values_splitted[i])
                if len(rec) > 1:
                    rec = rec[0]
                if not rec:
                    return None
                i += 1
            if not isinstance(rec._fields[values_splitted[i]], (fields.Boolean, fields.Float, fields.Monetary,
                                                                fields.Integer)):
                return None
        return value_converted

    def exec_python_code(self):
        self.ensure_one()
        locals_dict = self._get_eval_locals()
        exec(self.value, {'__builtins__': _BUILTINS}, locals_dict)
        return locals_dict

    def _get_eval_locals(self):
        locals_dict = {
            'calendar': calendar,
            'datetime': datetime,
            'dateutil': dateutil,
            'random': random,
            're': re,
            'time': time,
            'DEFAULT_SERVER_DATE_FORMAT': DEFAULT_SERVER_DATE_FORMAT,
            'DEFAULT_SERVER_TIME_FORMAT': DEFAULT_SERVER_TIME_FORMAT,
            'DEFAULT_SERVER_DATETIME_FORMAT': DEFAULT_SERVER_DATETIME_FORMAT,
            'self': self,
            'result': False,
        }
        return locals_dict
