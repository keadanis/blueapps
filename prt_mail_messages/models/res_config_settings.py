###################################################################################
# 
#    Copyright (C) Cetmix OÜ
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

from odoo import models, fields, api


###################
# Config Settings #
###################
class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    messages_easy_text_preview = fields.Integer(string="Text preview length")
    messages_easy_color_note = fields.Char(string="Note Background",
                                           help="Background color for internal notes in HTML format (e.g. #fbd78b)")

    # -- Save values
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        ICPSudo.set_param('cetmix.messages_easy_text_preview',
                          self.messages_easy_text_preview)
        ICPSudo.set_param('cetmix.messages_easy_color_note',
                          self.messages_easy_color_note)

    # -- Read values
    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()

        # Text preview length
        messages_easy_text_preview = ICPSudo.get_param('cetmix.messages_easy_text_preview', default=False)
        if messages_easy_text_preview:
            res.update(messages_easy_text_preview=int(messages_easy_text_preview))

        # Internal note background color
        messages_easy_color_note = ICPSudo.get_param('cetmix.messages_easy_color_note', default=False)
        if messages_easy_color_note:
            res.update(messages_easy_color_note=messages_easy_color_note)

        return res
