from odoo import models, fields, api
from datetime import date, datetime
from odoo.exceptions import UserError

class MedicalInpatientRegistration(models.Model):
    _inherit = 'medical.inpatient.registration'

    lab_test_history_ids = fields.One2many(
        'inpatient.lab.test.history',
        'inpatient_id',
        string='Test History'
    )

    treatment_history_ids = fields.One2many(
        'inpatient.treatment.history',
        'inpatient_id',
        string='Treatment History'
    )

    medicine_history_ids = fields.One2many(
        'inpatient.medicine.history',
        'inpatient_id',
        string='Medicine History'
    )

    bed_transfers_ids = fields.One2many(
        'bed.transfer',
        'inpatient_id',
        string='Admission History'
    )

    # total_history_amount = fields.Float(
    #     string="Total",
    #     compute="_compute_total_history_amount",
    #     store=True,
    # )

    treatment_medicine_total = fields.Float(
        string="Total",
        compute="_compute_treatment_medicine_total",
        store=True,
    )

    lab_test_total = fields.Integer(
        string="Lab Test Total",
        compute="_compute_lab_test_total",
        store=True,
    )
    ward_med_total = fields.Integer(
        string="Ward Med Total",
        compute="_compute_ward_med_total",
        store=True,
    )

    doctor_total = fields.Integer(string="Doctor Total")

    grand_total = fields.Float(
        string="Grand Total",
        compute="_compute_grand_total",
        store=True,
    )
    doctor_share_paid = fields.Boolean(string="Doctor Share Paid", default=False)
    doctor_bill_ids = fields.One2many(
        'account.move',
        'inpatient_registration_id',
        string='Doctor Bills'
    )
    doctor_bill_count = fields.Integer(
        string="Doctor Bill Count",
        compute="_compute_doctor_bill_count",
    )

    @api.depends('doctor_bill_ids')
    def _compute_doctor_bill_count(self):
        for rec in self:
            rec.doctor_bill_count = len(rec.doctor_bill_ids)

    def action_view_doctor_bills(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('account.action_move_in_invoice_type')
        action['domain'] = [('inpatient_registration_id', '=', self.id)]
        action['context'] = {'default_move_type': 'in_invoice'}
        return action

    def action_pay_doctor_share(self):
        self.ensure_one()
        if not self.attending_physician_id or not self.attending_physician_id.partner_id:
            raise UserError(_('No attending physician / vendor found.'))

        product = self.env['product.product'].search(
            [('is_doctor_share', '=', True)], limit=1
        )
        if not product:
            raise UserError(_('No product configured with Doctor Share.'))

        purchase_journals = self.env['account.journal'].search([('type', '=', 'purchase')], limit=1)

        bill_vals = {
            'move_type': 'in_invoice',
            'partner_id': self.attending_physician_id.partner_id.id,
            'journal_id': purchase_journals.id if purchase_journals else False,
            'invoice_date': date.today(),
            'inpatient_registration_id': self.id,
            'invoice_line_ids': [(0, 0, {
                'name': product.name,
                'product_id': product.id,
                'quantity': 1,
                'price_unit': self.doctor_total,
            })],
        }
        self.env['account.move'].create(bill_vals)
        self.doctor_share_paid = True

    def reset_to_draft(self):
        self.write({'state': 'hospitalized'})

    @api.depends("lab_test_history_ids.amount")
    def _compute_lab_test_total(self):
        for rec in self:
            rec.lab_test_total = sum(rec.lab_test_history_ids.mapped("amount"))

    @api.depends("medicine_history_ids.amount")
    def _compute_ward_med_total(self):
        for rec in self:
            rec.ward_med_total = sum(rec.medicine_history_ids.mapped("amount"))

    @api.depends("treatment_history_ids.amount", "medicine_history_ids.amount")
    def _compute_treatment_medicine_total(self):
        for rec in self:
            rec.treatment_medicine_total = (
                    sum(rec.treatment_history_ids.mapped("amount"))
                    + sum(rec.medicine_history_ids.mapped("amount"))
                    + sum(rec.lab_test_history_ids.mapped("amount"))
            )

    @api.depends("treatment_medicine_total", "lab_test_total", "ward_med_total", "doctor_total")
    def _compute_grand_total(self):
        for rec in self:
            rec.grand_total = (
                    rec.treatment_medicine_total
                    - rec.lab_test_total
                    - rec.ward_med_total
                    - rec.doctor_total
            )

    def patient_discharge(self):
        for record in self:
            record.write({'state': 'done'})

            invoices = self.env['account.move'].search([
                ('partner_id', '=', record.patient_id.patient_id.id),
                ('move_type', '=', 'out_invoice'),
                ('state', '!=', 'cancel'),
                ('invoice_date', '>=', record.hospitalization_date.date()),
                ('invoice_date', '<=', record.discharge_date.date()),
            ])

            record.treatment_history_ids.unlink()
            record.medicine_history_ids.unlink()
            record.lab_test_history_ids.unlink()

            regular_invoices = invoices.filtered(
                lambda inv: not inv.pos_order_ids
            )
            pos_invoices = invoices.filtered(
                lambda inv: inv.pos_order_ids
            )

            lab_invoices = regular_invoices.filtered(lambda inv: inv.is_lab_test)
            treatment_invoices = regular_invoices.filtered(lambda inv: not inv.is_lab_test)

            for line in treatment_invoices.mapped('invoice_line_ids'):
                self.env['inpatient.treatment.history'].create({
                    'inpatient_id': record.id,
                    'date': line.move_id.invoice_date,
                    'description': line.name,
                    'qty': line.quantity,
                    'unit_price': line.price_unit,
                    'disc_amt': (line.price_unit * line.quantity) * (line.discount or 0) / 100,
                    'amount': line.price_subtotal,
                })

            for line in lab_invoices.mapped('invoice_line_ids'):
                self.env['inpatient.lab.test.history'].create({
                    'inpatient_id': record.id,
                    'date': line.move_id.invoice_date,
                    'description': line.name,
                    'qty': line.quantity,
                    'unit_price': line.price_unit,
                    'disc_amt': (line.price_unit * line.quantity) * (line.discount or 0) / 100,
                    'amount': line.price_subtotal,
                })

            for line in pos_invoices.mapped('invoice_line_ids'):
                self.env['inpatient.medicine.history'].create({
                    'inpatient_id': record.id,
                    'date': line.move_id.invoice_date,
                    'description': line.name,
                    'qty': line.quantity,
                    'unit_price': line.price_unit,
                    'disc_amt': (line.price_unit * line.quantity) * (line.discount or 0) / 100,
                    'amount': line.price_subtotal,
                })

    # def patient_discharge_slip(self):
    #     self.ensure_one()
    #     Wizard = self.env.get('discharge.slip.wizard')
    #     if Wizard is None:
    #         return
    #     wizard = Wizard.create({
    #         'date_from': self.hospitalization_date.date(),
    #         'date_to': self.discharge_date.date(),
    #         'patient_id': self.patient_id.id,
    #         'inpatient_registration_id': self.id,
    #     })
    #     report = self.env.ref('xbo_mmh_report.action_discharge_slip_report', raise_if_not_found=False)
    #     if not report:
    #         return
    #     return report.report_action(wizard)
    #
    # def hospital_discharge_slip(self):
    #     self.ensure_one()
    #     Wizard = self.env.get('discharge.slip.wizard')
    #     if Wizard is None:
    #         return
    #     wizard = Wizard.create({
    #         'date_from': self.hospitalization_date.date(),
    #         'date_to': self.discharge_date.date(),
    #         'patient_id': self.patient_id.id,
    #         'inpatient_registration_id': self.id,
    #         'treatment_medicine_total': self.treatment_medicine_total,
    #         'lab_test_total': self.lab_test_total,
    #         'ward_med_total': self.ward_med_total,
    #         'doctor_total': self.doctor_total,
    #         'grand_total': self.grand_total,
    #     })
    #     report = self.env.ref('xbo_mmh_report.action_hospital_discharge_slip_report', raise_if_not_found=False)
    #     if not report:
    #         return
    #     return report.report_action(wizard)


class InpatientTreatmentHistory(models.Model):
    _name = 'inpatient.treatment.history'
    _description = 'Inpatient Treatment History'

    inpatient_id = fields.Many2one(
        'medical.inpatient.registration',
        ondelete='cascade'
    )
    date = fields.Date()
    description = fields.Char()
    qty = fields.Float()
    unit_price = fields.Float()
    disc_amt = fields.Float(string="Disc.Amt")
    amount = fields.Float()


class InpatientMedicineHistory(models.Model):
    _name = 'inpatient.medicine.history'
    _description = 'Inpatient Medicine History'

    inpatient_id = fields.Many2one(
        'medical.inpatient.registration',
        ondelete='cascade'
    )
    date = fields.Date()
    description = fields.Char()
    qty = fields.Float()
    unit_price = fields.Float()
    disc_amt = fields.Float(string="Disc.Amt")
    amount = fields.Float()


class InpatientLabTestHistory(models.Model):
    _name = 'inpatient.lab.test.history'
    _description = 'Inpatient Lab Test History'

    inpatient_id = fields.Many2one(
        'medical.inpatient.registration',
        ondelete='cascade'
    )
    date = fields.Date()
    description = fields.Char()
    qty = fields.Float()
    unit_price = fields.Float()
    disc_amt = fields.Float(string="Disc.Amt")
    amount = fields.Float()
