from odoo import fields, models


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    # Adicionado contadores para ordens de serviços agendados, para agendar.
    agendadas_count = fields.Integer(compute="_compute_agendadas_count", string="Total OS Agendadas")
    reagendadas_count = fields.Integer(compute="_compute_reagendadas_count", string="Total OS Reagendadas")
    abertas_count = fields.Integer(compute="_compute_abertas_count", string="Total OS Abertas")
    order_need_assign_count = fields.Integer(compute="_compute_order_need_assign_count", string="Total OS para Atríbuir")
    order_need_schedule_count = fields.Integer(compute="_compute_order_need_schedule_count", string="Total OS para Agendar")

    ## Diego ## 26/07/2021 "stage_id", "=", 16
    def _compute_agendadas_count(self):
        order_data = self.env["project.task"].read_group(
            [("stage_id", "in", self.ids), ("stage_id", "=", 10 )],
            ["stage_id"],
            ["stage_id"],
        )
        result = {data["stage_id"][0]: int(data["stage_id_count"]) for data in order_data}
        for task in self:
            task.agendadas_count = result.get(task.id, 0)

    def _compute_reagendadas_count(self):
        order_data = self.env["project.task"].read_group(
            [("stage_id", "in", self.ids), ("stage_id", "=", 11 )],
            ["stage_id"],
            ["stage_id"],
        )
        result = {data["stage_id"][0]: int(data["stage_id_count"]) for data in order_data}
        for task in self:
            task.reagendadas_count = result.get(task.id, 0)


    def _compute_abertas_count(self):
        order_data = self.env["project.task"].read_group(
            [("stage_id", "in", self.ids), ("stage_id", "=", 	13)],
            ["stage_id"],
            ["stage_id"],
        )
        result = {data["stage_id"][0]: int(data["stage_id_count"]) for data in order_data}
        for task in self:
            task.abertas_count = result.get(task.id, 0)

    def _compute_order_need_assign_count(self):
        order_data = self.env["project.task"].read_group(
            [("stage_id", "in", self.ids), ("user_id", "=", False)],
            ["stage_id"],
            ["stage_id"],
        )
        result = {data["stage_id"][0]: int(data["stage_id_count"]) for data in order_data}
        for task in self:
            task.order_need_assign_count = result.get(task.id, 0)

    def _compute_order_need_schedule_count(self):
        order_data = self.env["project.task"].read_group(
            [("stage_id", "in", self.ids), ("date_deadline", "=", False)],
            ["stage_id"],
            ["stage_id"],
        )
        result = {data["stage_id"][0]: int(data["stage_id_count"]) for data in order_data}
        for task in self:
            task.order_need_schedule_count = result.get(task.id, 0)