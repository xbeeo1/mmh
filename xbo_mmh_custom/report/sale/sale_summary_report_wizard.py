# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import timedelta, date, datetime


class SaleSummaryReport(models.TransientModel):
    _name = "sale.summary.report"
    _description = "Sale Summary Report"

    date_from = fields.Date(string="Date/Time From", default=date.today())
    date_to = fields.Date(string="Date/Time To", default=date.today())
    sale_purchase = fields.Selection(string="Sale/Purchase", selection=[('sale', 'Sale'), ('purchase', 'Purchase')],default='sale')
    report_type = fields.Selection(string="Type", selection=[('summary', 'Summary'), ('detail', 'Detail')], default='summary')


    def action_print_sale_summary_report(self):
        data = {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'sale_purchase': self.sale_purchase,
            'report_type': self.report_type,
        }
        return self.env.ref('xbo_mmh_custom.action_pdf_sale_summary_report').report_action(self.id)



    def action_print_sale_summary_report_xlsx(self):
        data = {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'sale_purchase': self.sale_purchase,
            'report_type': self.report_type,
        }
        return self.env.ref('xbo_mmh_custom.pos_cashier_xlsx_report').report_action(self.id)

