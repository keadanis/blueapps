# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class AccountTransaction(models.Model):
    _inherit = 'account.bank.statement.line'
    
    
    def _select(self):
        return """
            SELECT
                a.id,
                l.id as lead_id,
                l.user_id,
                l.team_id,
                l.country_id,
                l.company_id,
                l.stage_id,
                l.partner_id,
                l.type as lead_type,
                l.active,
                l.probability
        """

    def _from(self):
        return """
            FROM expense_summary AS e
        """

    def _join(self):
        return """
            INNER JOIN account_journal AS a ON e.account_journal_id = a.id
        """

    def _where(self):
        return """
            WHERE
                m.model = 'crm.lead' AND m.mail_activity_type_id IS NOT NULL
        """

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                %s
                %s
                %s
                %s
            )
        """ % (self._table, self._select(), self._from(), self._join(), self._where())
        )
