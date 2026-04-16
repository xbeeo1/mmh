# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta
from odoo import fields, models
from datetime import date, datetime, timedelta  # Add datetime here
from odoo import models, fields, api
from datetime import datetime, date, timedelta
from collections import defaultdict


class ReportSale(models.AbstractModel):
    _name = 'report.xbo_mmh_custom.sale_summary_xlsx_report'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):

        report_name = 'Sale Summary Report'
        body_data_left = workbook.add_format({'font_size': 11, "bold": False, "align": "left"})
        body_data_center = workbook.add_format({'font_size': 11, "bold": False, "align": "center"})
        header_line_left = workbook.add_format({'font_size': 11, "bold": True, "align": "left"})
        header_line_center = workbook.add_format({'font_size': 11, "bold": True, "align": "center"})
        header_format = workbook.add_format({'font_size': 13, "bold": True, 'bg_color': '#ffc404', "align": "center"})

        sheet = workbook.add_worksheet(report_name)
        sheet.set_column(0, 25, 25)

        for obj in lines:
            date_from = obj.date_from
            date_to = obj.date_to
            report_type = obj.report_type
            move_type = obj.sale_purchase
            # print('date_from', date_from, 'date_to', date_to, 'report_type', report_type)

            # PREPARE FILTER DOMAIN
            domain = [('create_date', '>=', date_from), ('create_date', '<=', date_from)]
            if move_type == 'sale':
                domain.append(('move_type', '=', 'out_invoice'))
            if move_type == 'purchase':
                domain.append(('move_type', '=', 'in_invoice'))
            invoices = self.env['account.move'].search(domain)

            # print('domain', domain)
            # print('invoices', invoices)

            if report_type == 'summary':
                # Initialize a dictionary for department-wise sums
                department_sums = defaultdict(lambda: {'total': 0.0, 'amount_due': 0.0, 'untaxed_amount': 0.0})

                for inv in invoices:
                    department_id = inv.department_id.name if inv.department_id else 'N/A'
                    department_sums[department_id]['total'] += inv.amount_total_in_currency_signed
                    department_sums[department_id]['amount_due'] += inv.amount_residual_signed
                    department_sums[department_id]['untaxed_amount'] += inv.amount_untaxed_in_currency_signed

                # Convert the results into a list of dictionaries
                summary_report_data = [
                    {
                        'department_id': dept_id,
                        'untaxed_amount': data['untaxed_amount'],
                        'total': data['total'],
                        'amount_due': data['amount_due']
                    }
                    for dept_id, data in department_sums.items()
                ]

                # Print the department-wise data
                # print('Department-wise sums:', summary_report_data)


                date_merge = 'Sale Summary Report From' + ' ' + str(date_from) + ' ' +  'to' + ' ' + str(date_to)
                sheet.merge_range('A1:D1', date_merge, header_format)

                if summary_report_data:
                    row = 2

                    sheet.write(row, 0, 'DEPARTMENT', header_line_left)
                    sheet.write(row, 1, 'TAX EXCLUDE', header_line_center)
                    sheet.write(row, 2, 'TOTAL', header_line_center)
                    sheet.write(row, 3, 'AMOUNT DUE', header_line_center)
                    row += 1

                    total_untaxed_amount = 0
                    total_amount = 0
                    total_amount_due = 0
                    for line in summary_report_data:
                        total_untaxed_amount += line.get('untaxed_amount')
                        total_amount += line.get('total')
                        total_amount_due += line.get('amount_due')
                        sheet.write(row, 0, line.get('department_id'), body_data_left)
                        sheet.write(row, 1, line.get('untaxed_amount'), body_data_center)
                        sheet.write(row, 2, line.get('total'), body_data_center)
                        sheet.write(row, 3, line.get('amount_due'), body_data_center)
                        row += 1

                    sheet.write(row, 0, 'TOTAL', header_line_left)
                    sheet.write(row, 1, total_untaxed_amount, header_line_center)
                    sheet.write(row, 2, total_amount, header_line_center)
                    sheet.write(row, 3, total_amount_due, header_line_center)
                    row += 1

            else:

                date_merge = 'Sale Details Report From' + ' ' + str(date_from) + ' ' + 'to' + ' ' + str(date_to)
                sheet.merge_range('A1:D1', date_merge, header_format)

                if invoices:
                    row = 2

                    discount_amount = 0
                    total_qty = 0
                    total_amount = 0
                    for inv in invoices:
                        # name = str(inv.name) + ' ' + str(inv.invoice_date)
                        sheet.write(row, 0, inv.name, header_line_left)
                        sheet.write(row, 1, str(inv.invoice_date), header_line_center)
                        sheet.write(row, 2, inv.department_id.name, header_line_center)
                        sheet.write(row, 3, inv.partner_id.name, header_line_center)
                        sheet.write(row, 4, inv.amount_total_in_currency_signed, header_line_center)
                        row += 1

                        for line in inv.invoice_line_ids:
                            print('product.....', line.product_id.name)
                            # name = str(inv.name) + ' ' + str(inv.invoice_date)
                            sheet.write(row, 0, line.product_id.name, body_data_left)
                            sheet.write(row, 1, line.quantity, body_data_center)
                            total_qty += line.quantity
                            sheet.write(row, 2, line.price_unit, body_data_center)
                            sheet.write(row, 3, line.discount, body_data_center)
                            subtotal = line.price_unit * line.quantity
                            discount_amount += (subtotal /100) * line.discount
                            sheet.write(row, 4, line.price_total, body_data_center)
                            total_amount += line.price_total
                            row += 1

                    sheet.write(row, 0, 'TOTAL', header_line_left)
                    sheet.write(row, 1, total_qty, header_line_center)
                    sheet.write(row, 2, '-', header_line_center)
                    sheet.write(row, 3, discount_amount, header_line_center)
                    sheet.write(row, 4, total_amount, header_line_center)
                    row += 1

