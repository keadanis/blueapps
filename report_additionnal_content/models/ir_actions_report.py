# Copyright Sudokeys (www.sudokeys.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
import os
import tempfile

from PyPDF2 import PdfFileMerger, PdfFileReader, PdfFileWriter

from odoo import api, fields, models


class ActionReport(models.Model):
    _inherit = "ir.actions.report"

    additionnal_line_ids = fields.One2many(
        comodel_name="ir.actions.report.line",
        inverse_name="action_report_id",
        string="Additionnal content",
    )
    watermark_file = fields.Binary(string="Watermark")
    watermark_filename = fields.Char(string="Watermark name")

    def _render_qweb_pdf(self, res_ids=None, data=None):
        self.ensure_one()
        if self.additionnal_line_ids or self.watermark_file:
            return super(
                ActionReport,
                self.with_context(additionnal_content=self, res_ids=res_ids),
            )._render_qweb_pdf(res_ids, data)
        else:
            return super(ActionReport, self)._render_qweb_pdf(res_ids, data)

    @api.model
    def _run_wkhtmltopdf(
        self,
        bodies,
        header=None,
        footer=None,
        landscape=False,
        specific_paperformat_args=None,
        set_viewport_size=False,
    ):
        report = super(ActionReport, self)._run_wkhtmltopdf(
            bodies,
            header,
            footer,
            landscape,
            specific_paperformat_args,
            set_viewport_size,
        )
        if self._context.get("additionnal_content", False):
            return self._add_additionnal_content(report)
        return report

    def _add_additionnal_content(self, report):
        model = self.env[self.model]
        fields = model._fields
        records = model.browse(id for id in self._context.get("res_ids", False))

        # Prepare additionnal content
        before_files = []
        after_files = []
        for content in self._context.get("additionnal_content").additionnal_line_ids:

            if self.env.user.company_id in content.company_ids:
                langs = content.lang_ids.mapped("code")

                if not langs:
                    # Company additionnal content
                    (
                        additionnal_content_fd,
                        additionnal_content_name,
                    ) = tempfile.mkstemp()
                    pdf = open(additionnal_content_name, "wb")
                    pdf.write(base64.b64decode(content.additionnal_content))
                    pdf.close()
                    if content.position == "be":
                        before_files.append(additionnal_content_name)
                    else:
                        after_files.append(additionnal_content_name)
                else:
                    # Company + lang additionnal content
                    if any("partner_id" == i for i in fields):
                        if any(
                            lang in langs for lang in records.mapped("partner_id.lang")
                        ):
                            (
                                additionnal_content_fd,
                                additionnal_content_name,
                            ) = tempfile.mkstemp()
                            pdf = open(additionnal_content_name, "wb")
                            pdf.write(base64.b64decode(content.additionnal_content))
                            pdf.close()
                            if content.position == "be":
                                before_files.append(additionnal_content_name)
                            else:
                                after_files.append(additionnal_content_name)

        # Prepare initial content
        original_report_fd, original_report_name = tempfile.mkstemp()
        pdf = open(original_report_name, "wb")
        pdf.write(report)
        pdf.close()
        # Merge watermark
        watermark_file = self._context.get("additionnal_content").watermark_file
        if watermark_file:
            watermark_fd, watermark_name = tempfile.mkstemp()
            pdf = open(watermark_name, "wb")
            pdf.write(base64.b64decode(watermark_file))
            pdf.close()
            watermark = PdfFileReader(open(watermark_name, "rb"))
            original = PdfFileReader(open(original_report_name, "rb"))
            new_report = PdfFileWriter()
            for page_num in range(original.getNumPages()):
                page = watermark.getPage(0)
                page.mergePage(original.getPage(page_num))
                new_report.addPage(page)
            new_report_fd, watermark_report_name = tempfile.mkstemp()
            pdf = open(watermark_report_name, "wb")
            new_report.write(pdf)
            pdf.close()
            os.remove(watermark_name)
        # Merge
        merger = PdfFileMerger()
        end_result_fd, end_result_name = tempfile.mkstemp()
        for content in before_files:
            merger.append(PdfFileReader(open(content, "rb")), import_bookmarks=False)
        if watermark_file:
            merger.append(
                PdfFileReader(open(watermark_report_name, "rb")), import_bookmarks=False
            )
        else:
            merger.append(
                PdfFileReader(open(original_report_name, "rb")), import_bookmarks=False
            )
        for content in after_files:
            merger.append(PdfFileReader(open(content, "rb")), import_bookmarks=False)
        merger.write(end_result_name)
        pdf = open(end_result_name, "rb")
        res = pdf.read()
        pdf.close()
        # Clean
        for content in before_files:
            os.remove(content)
        for content in after_files:
            os.remove(content)
        if watermark_file:
            os.remove(watermark_report_name)
        os.remove(original_report_name)
        os.remove(end_result_name)
        return res
