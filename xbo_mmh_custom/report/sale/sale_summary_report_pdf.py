# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta
from odoo import fields, models
from datetime import date, datetime, timedelta  # Add datetime here
from odoo import models, fields, api
from datetime import datetime, date, timedelta
from collections import defaultdict


class ConsolidateReportPdf(models.AbstractModel):
    _name = 'report.xbo_mmh_custom.sale_summary_template'
    _description = "Employee Payslips Report ID"

    @api.model
    def _get_report_values(self, docids, data=None):

        wizard_data = self.env['sale.summary.report'].browse(self._context.get('active_id'))

        date_from = wizard_data.date_from
        date_to = wizard_data.date_to
        report_type = wizard_data.report_type
        move_type = wizard_data.sale_purchase

        # Combine date_from with minimum time
        date_from_dt = datetime.combine(date_from, datetime.min.time())
        # Combine date_to with end-of-day time (23:59:59)
        date_to_dt = datetime.combine(date_to, datetime.max.time()).replace(second=59, microsecond=0)

        # print('date_from_dt:', date_from_dt, 'date_to_dt:', date_to_dt)

        # Add 5 hours to both date_from and date_to
        date_from_plus_5hrs = (date_from_dt + timedelta(hours=5)).replace(hour=0, minute=0, second=0, microsecond=0)
        date_to_plus_5hrs = (date_to_dt + timedelta(hours=5)).replace(hour=23, minute=59, second=59, microsecond=0)

        # print(f"Date From + 5 Hours (datetime): {date_from_plus_5hrs}")
        # print(f"Date To + 5 Hours (datetime): {date_to_plus_5hrs}")



        # PREPARE FILTER DOMAIN
        domain = [('create_date', '>=', date_from),('create_date', '<=', date_to)]
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


            return {
                'date_from': date_from,
                'date_to': date_to,
                'move_type': move_type,
                'report_type': 'Summary',
                'summary_report_data': summary_report_data,
            }

        else:

            return {
                'date_from': date_from,
                'date_to': date_to,
                'move_type': move_type,
                'report_type': 'Details',
                'invoices': invoices,
            }



