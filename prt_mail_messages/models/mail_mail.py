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

from odoo import models


#############
# Mail.Mail #
#############
class MailMail(models.Model):
    _inherit = "mail.mail"

    # -- Post process sent mail messages
    def _postprocess_sent_message(
        self, success_pids, failure_reason=False, failure_type=None
    ):
        # Save messages to be deleted.
        # Mark them as NOT auto delete because we want to delete them via messages
        mail_to_delete_ids = [mail.id for mail in self if mail.auto_delete]
        if len(mail_to_delete_ids) > 0:
            mark_to_delete = self.sudo().browse(mail_to_delete_ids)
            mark_to_delete.write({"auto_delete": False})

        res = super(MailMail, self)._postprocess_sent_message(
            success_pids, failure_reason, failure_type
        )

        # Delete related messages so they will trigger
        # cascade mail.mail deletion
        if len(mail_to_delete_ids) > 0:
            mark_to_delete.write({"is_mail_mail": True})
            mark_to_delete.unlink()

        return res
