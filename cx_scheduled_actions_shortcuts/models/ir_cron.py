###################################################################################
# 
#    Copyright (C) 2020 Cetmix OÜ
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU LESSER GENERAL PUBLIC LICENSE as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###################################################################################

from odoo import _, api, fields, models
from odoo.exceptions import AccessError


class CetmixInheritIrCron(models.Model):
    _inherit = "ir.cron"

    # Basic fields example
    shortcut_group_ids = fields.Many2many(
        string="Shortcut Groups",
        help="Add system tray shortcut for the following groups",
        comodel_name="res.groups",
    )
    shortcut_name = fields.Char(
        string="Shortcut Name",
        help="Shortcut caption. Action name will be used if empty",
    )

    # -- Get shortcuts
    @api.model
    def get_shortcuts(self):
        return self.sudo().search_read(
            [("shortcut_group_ids", "in", self.env.user.groups_id.ids)],
            ["name", "shortcut_name"],
        )

    # -- Run action
    def run_shortcut_action(self):
        for rec in self:
            if not self.env.user.groups_id.ids not in (rec.shortcut_group_ids.ids):
                raise AccessError(
                    _("You are not allowed to run actions using shortcuts!")
                )
        return self.sudo().method_direct_trigger()
