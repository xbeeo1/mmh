from odoo import models, fields

class CustomerBalanceReport(models.AbstractModel):
    _name = 'report.xbo_mmh_report.customer_balance_report_template'
    _description = 'Customer Balance Report'

    def _get_report_values(self, docids, data=None):
        date_from = fields.Date.from_string(data.get('date_from'))
        date_to = fields.Date.from_string(data.get('date_to'))
        return {
            'date_from': date_from.strftime('%d-%m-%Y'),
            'date_to': date_to.strftime('%d-%m-%Y'),
            'lines': data.get('lines'),
            'company': self.env.company,
        }


class VendorBalanceReport(models.AbstractModel):
    _name = 'report.xbo_mmh_report.vendor_balance_report_template'
    _description = 'Vendor Balance Report'

    def _get_report_values(self, docids, data=None):
        date_from = fields.Date.from_string(data.get('date_from'))
        date_to = fields.Date.from_string(data.get('date_to'))
        return {
            'date_from': date_from.strftime('%d-%m-%Y'),
            'date_to': date_to.strftime('%d-%m-%Y'),
            'lines': data.get('lines'),
            'company': self.env.company,
        }