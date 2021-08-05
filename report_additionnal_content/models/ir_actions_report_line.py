# Copyright Sudokeys (www.sudokeys.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models

POSITION_OPT = [
    ("be", _("Before")),
    ("af", _("After")),
]


class ActionReportLine(models.Model):
    _name = "ir.actions.report.line"
    _description = "Report Action Line"
    _order = "sequence ASC"

    name = fields.Char(string="Name")
    sequence = fields.Integer(string="Sequence")
    additionnal_content = fields.Binary(string="Additionnal Content", required=True)
    position = fields.Selection(
        selection=POSITION_OPT, string="Position", required=True, default="af"
    )
    action_report_id = fields.Many2one(
        comodel_name="ir.actions.report", string="Action Report", required=True
    )
    company_ids = fields.Many2many(comodel_name="res.company", string="Companies")
    lang_ids = fields.Many2many(comodel_name="res.lang", string="Languages")
