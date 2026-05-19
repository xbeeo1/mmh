from odoo import models

class ReportPartnerLedger(models.AbstractModel):
    _inherit = 'report.accounting_pdf_reports.report_partnerledger'

    def _lines(self, data, partner):
        lines = super()._lines(data, partner)

        for line in lines:
            move_line = self.env['account.move.line'].browse(line['id'])

            line['description'] = move_line.description or ''

        return lines