# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import date,datetime,timedelta

class MedicalLabInherit(models.Model):
    _inherit = "medical.lab"
    _description = 'medical.lab Inherit'

    invoice_count = fields.Integer(string="Journal Entries", compute='_invoice_total')
    amount_invoice = fields.Float(string="Amount", compute='_invoice_total')
    patient_type_id = fields.Many2one("patient.type", string="Patient Type", related='patient_id.patient_id.patient_type_id', store=True)
    patient_mobile = fields.Char(string="Mobile", related='patient_id.patient_mobile', store=True)
    patient_cnic = fields.Char(string="CNIC", related='patient_id.patient_cnic', store=True)
    mr_number = fields.Char(string="MR Number", related='patient_id.name', store=True)
    move_id = fields.Many2one("account.move", string="Invoice",)


    """COUNT ALL RELATED INVOICES"""

    def _invoice_total(self):
        for rec in self:
            invoice_count = rec.env['account.move'].search_count([('partner_id', '=', rec.patient_id.patient_id.id), ('invoice_origin', 'ilike', rec.name)])
            rec.invoice_count = invoice_count
            invoice = rec.env['account.move'].search([('partner_id', '=', rec.patient_id.patient_id.id), ('invoice_origin', 'ilike', rec.name)])
            rec.amount_invoice = sum(inv['amount_total_in_currency_signed'] for inv in invoice)


    """VIEW ALL JOURNAL INVOICES"""
    def action_view_invoices(self):
        self.ensure_one()
        result = {
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "name": _("Invoice"),
            'view_mode': 'list,form',
            'domain': [('partner_id', '=', self.patient_id.patient_id.id), ('invoice_origin', 'ilike', self.name)],
        }
        return result

    def get_adjusted_date_requested(self):
        if self.date_requested:
            return self.date_requested + timedelta(hours=5)
        return self.date_requested

    def get_last_results(self):
        self.ensure_one()

        records = self.search([
            ('patient_id', '=', self.patient_id.id),
            ('test_id', '=', self.test_id.id),
            ('id', '<=', self.id)
        ], order='date_requested desc', limit=3)

        return records

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)

        for vals in vals_list:
            if vals.get('test_id'):
                test = self.env['medical.test_type'].browse(vals['test_id'])
                product = test.service_product_id

                if product and product.create_mrp_order:
                    bom_count = self.env['mrp.bom'].search([
                        ('product_tmpl_id', '=', product.product_tmpl_id.id)
                    ])

                    if bom_count:
                        bom_temp = self.env['mrp.bom'].search([
                            ('product_tmpl_id', '=', product.product_tmpl_id.id),
                            ('product_id', '=', False)
                        ])

                        bom_prod = self.env['mrp.bom'].search([
                            ('product_id', '=', product.id)
                        ])

                        if bom_prod:
                            bom = bom_prod[0]
                        elif bom_temp:
                            bom = bom_temp[0]
                        else:
                            bom = False

                        if bom:
                            mrp_vals = {
                                'origin': vals.get('name'),
                                'product_id': product.id,
                                'product_tmpl_id': product.product_tmpl_id.id,
                                'product_uom_id': product.uom_id.id,
                                'product_qty': 1,
                                'bom_id': bom.id,
                            }

                            mrp = self.env['mrp.production'].sudo().create(mrp_vals)

                            if product.done_mrp_order:
                                mrp.button_mark_done()

        return res