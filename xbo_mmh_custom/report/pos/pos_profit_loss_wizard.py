# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, date


class PosProfitLoss(models.TransientModel):
    _name = "pos.profit.loss.wizard"
    _description = "POS Profit & Loss"

    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date to')


    def print_pos_profit_loss_report(self):
        domain = []
        if self.date_from and self.date_to:
            domain.append(('date_order', '>=', self.date_from))
            domain.append(('date_order', '<=', self.date_to))

        docs = self.env['pos.order'].search(domain)

        if not docs:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Records Found'),
                    'message': _('No records match the selected filters.'),
                    'type': 'warning',
                    'sticky': False,
                },
            }
        datas = {
            'date_from': self.date_from,
            'date_to': self.date_to,
        }
        return self.env.ref('xbo_mmh_custom.action_pos_profit_loss_report').report_action(self, datas)



class action_pos_profit_loss_report(models.AbstractModel):
    _name = 'report.xbo_mmh_custom.report_pos_profit_loss'
    _description = 'POS Profit & Loss'

    @api.model
    def _get_report_values(self, docids, data):
        domain = []
        date_from = data['date_from']
        date_to = data['date_to']

        if isinstance(date_from, str):
            date_from = datetime.strptime(date_from, "%Y-%m-%d").date()
        if isinstance(date_to, str):
            date_to = datetime.strptime(date_to, "%Y-%m-%d").date()


        if date_from and date_to:
            domain.append(('date_order', '>=', date_from))
            domain.append(('date_order', '<=', date_to))
        docs = self.env['pos.order'].search(domain)
        return {
            'docs': docs,
            'date_from': date_from.strftime('%d-%m-%Y') if date_from else '',
            'date_to': date_to.strftime('%d-%m-%Y') if date_to else '',
        }


