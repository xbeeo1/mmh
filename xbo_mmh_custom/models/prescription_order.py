# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _, Command
from datetime import date,datetime
from odoo.exceptions import ValidationError

class MedicalPrescriptionOrderInherit(models.Model):
    _inherit = "medical.prescription.order"
    _description = 'medical Prescription order'


    invoice_count = fields.Integer(string="Journal Entries", compute='_invoice_total')
    amount_invoice = fields.Float(string="Amount", compute='_invoice_total')
    patient_id_name = fields.Char(string="Patient ID")
    treatment_fees = fields.Float(string="Treatment Fees", store=True)
    department_id = fields.Many2one("hr.department",related='patient_id.department_id',store=True, string="Department")
    patient_type_id = fields.Many2one("patient.type", string="Patient Type", related='patient_id.patient_id.patient_type_id', store=True)

    """COUNT ALL RELATED INVOICES"""
    def _invoice_total(self):
        for rec in self:
            invoice_count = self.env['account.move'].search_count([('invoice_origin', '=', rec.patient_id.name)])
            rec.invoice_count = invoice_count

            invoice = self.env['account.move'].search([('partner_id', '=', rec.patient_id.patient_id.id), ('invoice_origin', '=', rec.name)])
            rec.amount_invoice = sum(invoice.mapped('amount_total_in_currency_signed'))

    def action_print_patient_card(self):
        self.ensure_one()
        invoice_count = self.env['account.move'].search_count([('invoice_origin', '=', self.patient_id.name),('date','=',self.prescription_date.date())])
        if invoice_count > 0:
            return self.env.ref("xbo_mmh_custom.pre_report_print_patient_card").report_action(self.patient_id)
        else:
            raise ValidationError('Please create Invoice')

    """VIEW ALL JOURNAL INVOICES"""
    def action_view_invoices(self):
        self.ensure_one()
        result = {
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "name": _("Invoice"),
            'view_mode': 'list,form',
            'domain': [('invoice_origin', '=', self.patient_id.name)],
        }
        return result



    @api.onchange('doctor_id')
    def _onchange_doctor_id(self):

        if self.doctor_id:
            rate_id = self.env['treatment.rate.line'].search(
                [('doctor_id', '=', self.doctor_id.partner_id.id),
                 ('treatment_type_id', '=', self.patient_id.treatment_type_id.id)], limit=1)

            # doctor_treatment_type = self.doctor_id.partner_id.treatment_type_id.id
            #
            # if doctor_treatment_type:
            #
            #     for tl in self.doctor_id.partner_id.department_id.treatment_rate_line:
            #
            #         if tl.treatment_type_id.id == self.patient_id.patient_id.treatment_type_id.id:
            #             # print('Patient : ', self.patient_id.patient_id.name, 'Patient treatment type : ', self.patient_id.patient_id.treatment_type_id.name)
            #             # print('Doctor Department : ', self.doctor_id.partner_id.department_id.name, 'Doctor : ', self.doctor_id.partner_id.name, 'Patient treatment type : ', self.patient_id.patient_id.treatment_type_id.name, 'Treatment fees : ', tl.treatment_fees)
            #             self.treatment_fees = tl.treatment_fees
            self.treatment_fees = rate_id.treatment_fees



    def action_create_prescription_invoice(self):
        move_lines = []
        for line in self.prescription_line_ids:
            move_lines.append(Command.create({
                'product_id': line.medicament_id.product_id.id,
                'name': line.medicament_id.product_id.display_name or '',
                'quantity': line.quantity,
                'price_unit': line.medicament_id.product_id.lst_price,
                'product_uom_id': line.medicament_id.product_id.uom_id.id,

            }),
            )

        # print('move_lines........', move_lines)

        # Create journal entry
        move = self.env['account.move'].create({
            # 'name': self.env['ir.sequence'].next_by_code('pres_inv_seq'),
            'move_type': 'out_invoice',
            'ref': self.name,
            'invoice_origin': self.patient_id.name or '',
            'date': date.today(),
            'partner_id': self.patient_id.patient_id.id,
            'doctor_id': self.doctor_id.partner_id.id,
            'department_id': self.department_id.id,
            'patient_type_id': self.patient_id.patient_id.patient_type_id.id,
            'invoice_line_ids': move_lines,
        })

        # print('move.....', move.name)




