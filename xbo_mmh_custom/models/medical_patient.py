# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo import models, fields, api, Command
from odoo.exceptions import ValidationError
from odoo.osv import expression
import calendar
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

class MedicalPatientInherit(models.Model):
    _inherit = 'medical.patient'

    treatment_type_id = fields.Many2one("treatment.type", string="Treatment Type", related='patient_id.treatment_type_id',store=True)
    patient_mobile = fields.Char(string="Mobile", related='patient_id.phone',store=True)
    patient_cnic = fields.Char(string="CNIC", related='patient_id.patient_cnic',store=True)
    village_id = fields.Many2one("patient.village",related='patient_id.village_id',store=True, string="Village")
    medical_patient_type_id = fields.Many2one("patient.type",related='patient_id.patient_type_id',store=True, string="Patient Type")
    department_id = fields.Many2one("hr.department", string="Department")

    treatment_fees = fields.Float(string="Treatment Fees", compute='_compute_doctor_treatment_fees')

    prescription_count = fields.Integer(string="Prescriptions", compute='_prescription_total')
    invoice_count = fields.Integer(string="Invoice", compute='_invoices_total')



    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        result = []
        # if not name:
        #     return super(MedicalPatientInherit, self).name_search(
        #         name=name, args=args, operator=operator, limit=limit
        #     )
        mr_patients = self.search(expression.AND([args, [('name', operator, name)]]), limit=limit)
        result.extend((p.id, p.name) for p in mr_patients)
        remaining_limit = limit - len(result) if limit else None

        if remaining_limit is not None and remaining_limit <= 0:
            return result

        # Step 2: Search by partner name or mobile
        partner_ids = self.env['res.partner'].search([
            '|','|',
            ('name', operator, name),
            ('phone', operator, name),
            ('patient_cnic', operator, name)
        ]).ids

        if partner_ids:
            patients = self.search(expression.AND([args, [('patient_id', 'in', partner_ids)]]),
                                   limit=remaining_limit)
            for p in patients:
                if p.id not in [r[0] for r in result]:
                    display_name = f"{p.name} - {p.patient_id.name or ''} - {p.patient_id.phone or ''} - {p.patient_id.patient_cnic or ''}"
                    result.append((p.id, display_name))

        return result


    @api.onchange('primary_care_physician_id')
    def _onchange_primary_care_physician(self):
        if self.primary_care_physician_id:
            self.patient_id.primary_care_physician_id = self.primary_care_physician_id.id
            self.department_id=self.primary_care_physician_id.partner_id.department_id.id

    @api.depends('department_id', 'primary_care_physician_id')
    def _compute_doctor_treatment_fees(self):
        for rec in self:
            rate_id = self.env['treatment.rate.line'].search([('doctor_id', '=', rec.primary_care_physician_id.partner_id.id),
                                                              ('treatment_type_id', '=', rec.treatment_type_id.id)], limit=1)
            print('rate_id', rate_id)
            rec.treatment_fees = rate_id.treatment_fees


    def action_create_invoice(self):
        print('Create Invoice....................')
        if not self.treatment_fees:
            raise ValidationError('You Cannot Create Invoice Without Fees')

        product_id = self.env['product.product'].search([('name', '=', self.treatment_type_id.name)], limit=1)
        move_lines = [
            Command.create({
                'product_id': product_id.id,
                'quantity': 1,
                'price_unit': self.treatment_fees,
            }),
        ]

        # Create journal entry
        move = self.env['account.move'].create({
            'name': self.env['ir.sequence'].next_by_code('medical_health_service_inv_seq'),
            'move_type': 'out_invoice',
            'ref': self.name,
            'date': date.today(),
            'partner_id': self.patient_id.id,
            'invoice_origin': self.patient_id.name,
            'doctor_id': self.primary_care_physician_id.partner_id.id,
            'department_id': self.department_id.id,
            'patient_type_id': self.medical_patient_type_id.id,
            'invoice_line_ids': move_lines,
        })

        print('Move...........', move.name)
        print('Move...........',  self.env['ir.sequence'].next_by_code('medical_health_service_inv_seq'))


    """COUNT ALL RELATED PRESCRIPTIONS"""
    def _invoices_total(self):
        for rec in self:
            invoice_count = self.env['account.move'].search_count([('partner_id', '=', rec.patient_id.id)])
            rec.invoice_count = invoice_count


    """VIEW ALL INVOICES"""
    def action_view_invoices(self):
        self.ensure_one()
        result = {
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "name": _("Invoice"),
            'view_mode': 'list,form',
            'domain': [('partner_id', '=', self.patient_id.id)],
        }
        return result



    """COUNT ALL RELATED PRESCRIPTIONS"""

    def _prescription_total(self):
        for rec in self:
            prescription_count = self.env['medical.prescription.order'].search_count([('patient_id', '=', rec.id)])
            rec.prescription_count = prescription_count


    """VIEW ALL PRESCRIPTIONS"""
    def action_view_prescriptions(self):
        self.ensure_one()
        result = {
            "type": "ir.actions.act_window",
            "res_model": "medical.prescription.order",
            "name": _("PRESCRIPTIONS"),
            'view_mode': 'list,form',
            'domain': [('patient_id', '=', self.id)],
        }
        return result

    def action_view_create_prescription(self):
        self.ensure_one()
        patient = self.env['medical.patient'].search([('patient_id', '=', self.patient_id.id)], limit=1)
        return {
            'name': _('Create Prescription'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'medical.prescription.order',
            'view_id': self.env.ref('basic_hms.medical_prescription_order_form_view').id,
            'context': {
                'default_patient_id': patient.id,
                'default_doctor_id': patient.primary_care_physician_id.id,
                'default_patient_id_name': patient.name,
            },
        }
