from odoo import models, fields,api


class MedicalInpatientRegistration(models.Model):
    _inherit = 'medical.inpatient.registration'

    def patient_discharge_slip(self):
        self.ensure_one()
        wizard = self.env['discharge.slip.wizard'].create({
            'date_from': self.hospitalization_date.date(),
            'date_to': self.discharge_date.date(),
            'patient_id': self.patient_id.id,
            'inpatient_registration_id': self.id,
        })
        return self.env.ref(
            'xbo_mmh_report.action_discharge_slip_report'
        ).report_action(wizard)

    def hospital_discharge_slip(self):
        self.ensure_one()
        wizard = self.env['discharge.slip.wizard'].create({
            'date_from': self.hospitalization_date.date(),
            'date_to': self.discharge_date.date(),
            'patient_id': self.patient_id.id,
            'inpatient_registration_id': self.id,
            'treatment_medicine_total': self.treatment_medicine_total,
            'lab_test_total': self.lab_test_total,
            'ward_med_total': self.ward_med_total,
            'doctor_total': self.doctor_total,
            'grand_total': self.grand_total,
        })
        return self.env.ref(
            'xbo_mmh_report.action_hospital_discharge_slip_report'
        ).report_action(wizard)

    # treatment_history_ids = fields.One2many(
    #     'inpatient.treatment.history',
    #     'inpatient_id',
    #     string='Treatment History'
    # )
    #
    # medicine_history_ids = fields.One2many(
    #     'inpatient.medicine.history',
    #     'inpatient_id',
    #     string='Medicine History'
    # )
    #
    # bed_transfers_ids = fields.One2many(
    #     'bed.transfer',
    #     'inpatient_id',
    #     string='Admission History'
    # )
    #
    # total_history_amount = fields.Float(
    #     string="Total",
    #     compute="_compute_total_history_amount",
    #     store=True,
    # )
    #
    # treatment_medicine_total = fields.Float(
    #     string="Treatment & Medicine Total",
    #     compute="_compute_treatment_medicine_total",
    #     store=True,
    # )
    #
    # lab_test_total = fields.Integer(string="Lab Test Total")
    # ward_med_total = fields.Integer(string="Ward Med Total")
    # doctor_total = fields.Integer(string="Doctor Total")
    # grand_total = fields.Float(
    #     string="Grand Total",
    #     compute="_compute_grand_total",
    #     store=True,
    # )
    #
    # @api.depends("treatment_history_ids.amount", "medicine_history_ids.amount")
    # def _compute_treatment_medicine_total(self):
    #     for rec in self:
    #         rec.treatment_medicine_total = (
    #                 sum(rec.treatment_history_ids.mapped("amount"))
    #                 + sum(rec.medicine_history_ids.mapped("amount"))
    #         )
    #
    # @api.depends("treatment_medicine_total", "lab_test_total", "ward_med_total", "doctor_total")
    # def _compute_grand_total(self):
    #     for rec in self:
    #         rec.grand_total = (
    #                 rec.treatment_medicine_total
    #                 + rec.lab_test_total
    #                 + rec.ward_med_total
    #                 + rec.doctor_total
    #         )
    #
    # def patient_discharge(self):
    #     for record in self:
    #         record.write({'state': 'done'})
    #
    #         invoices = self.env['account.move'].search([
    #             ('partner_id', '=', record.patient_id.patient_id.id),
    #             ('move_type', '=', 'out_invoice'),
    #             ('state', '!=', 'cancel'),
    #             ('invoice_date', '>=', record.hospitalization_date.date()),
    #             ('invoice_date', '<=', record.discharge_date.date()),
    #         ])
    #
    #         record.treatment_history_ids.unlink()
    #         record.medicine_history_ids.unlink()
    #
    #         regular_invoices = invoices.filtered(
    #             lambda inv: not inv.pos_order_ids
    #         )
    #         pos_invoices = invoices.filtered(
    #             lambda inv: inv.pos_order_ids
    #         )
    #
    #         for line in regular_invoices.mapped('invoice_line_ids'):
    #             self.env['inpatient.treatment.history'].create({
    #                 'inpatient_id': record.id,
    #                 'date': line.move_id.invoice_date,
    #                 'description': line.name,
    #                 'qty': line.quantity,
    #                 'unit_price': line.price_unit,
    #                 'amount': line.price_subtotal,
    #             })
    #
    #         for line in pos_invoices.mapped('invoice_line_ids'):
    #             self.env['inpatient.medicine.history'].create({
    #                 'inpatient_id': record.id,
    #                 'date': line.move_id.invoice_date,
    #                 'description': line.name,
    #                 'qty': line.quantity,
    #                 'unit_price': line.price_unit,
    #                 'amount': line.price_subtotal,
    #             })



# class InpatientTreatmentHistory(models.Model):
#     _name = 'inpatient.treatment.history'
#     _description = 'Inpatient Treatment History'
#
#     inpatient_id = fields.Many2one(
#         'medical.inpatient.registration',
#         ondelete='cascade'
#     )
#     date = fields.Date()
#     description = fields.Char()
#     qty = fields.Float()
#     unit_price = fields.Float()
#     amount = fields.Float()
#
#
# class InpatientMedicineHistory(models.Model):
#     _name = 'inpatient.medicine.history'
#     _description = 'Inpatient Medicine History'
#
#     inpatient_id = fields.Many2one(
#         'medical.inpatient.registration',
#         ondelete='cascade'
#     )
#     date = fields.Date()
#     description = fields.Char()
#     qty = fields.Float()
#     unit_price = fields.Float()
#     amount = fields.Float()