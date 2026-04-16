# -*- coding: utf-8 -*-


from odoo import api, fields, models , _
from datetime import date, datetime


class OutsourcedLabRequest(models.Model):
    _name = 'outsourced.lab.request'
    _description = 'Outsourced Lab Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char("Name" , readonly=True)
    date_analysis = fields.Datetime('Date of the Analysis', default=datetime.now() , readonly=True)
    patient_id = fields.Many2one('medical.patient', 'Patient', readonly=True)
    patient_mobile = fields.Char(string="Mobile", related='patient_id.patient_mobile', store=True)
    patient_cnic = fields.Char(string="CNIC", related='patient_id.patient_cnic', store=True)
    mr_number = fields.Char(string="MR Number", related='patient_id.name', store=True)
    date_requested = fields.Datetime('Date requested', default=datetime.now() , readonly=True)
    requestor_physician_id = fields.Many2one('medical.physician', 'Physician',  readonly=True)
    partner_lab_id = fields.Many2one(comodel_name='partner.lab', string="Partner Lab" , readonly=True)
    is_invoiced = fields.Boolean(copy=False, default=False)
    outsourced_lab_test_lines = fields.One2many('outsourced.lab.test.line', 'outsourced_lab_test_id',
                                     string="Lab Test Line")
    state = fields.Selection([('draft', 'Draft'),
                              ('sample_submitted', 'Sample Submitted'),
                              ('reports_received', 'Reports Received'),
                              ('delivered', 'Delivered')],
                             string='Status', readonly=True, default='draft')

    invoice_count = fields.Integer(string="Journal Entries", compute='_invoice_total')
    amount_invoice = fields.Float(string="Amount", compute='_invoice_total')
    patient_type_id = fields.Many2one("patient.type", string="Patient Type",
                                      related='patient_id.patient_id.patient_type_id', store=True)
    move_id = fields.Many2one("account.move", string="Invoice", )

    """COUNT ALL RELATED INVOICES"""

    def _invoice_total(self):
        for rec in self:
            invoice_count = rec.env['account.move'].search_count(
                [('partner_id', '=', rec.patient_id.patient_id.id), ('invoice_origin', 'ilike', rec.name),('outsourced_lab_request','=',True)])
            rec.invoice_count = invoice_count
            invoice = rec.env['account.move'].search(
                [('partner_id', '=', rec.patient_id.patient_id.id), ('invoice_origin', 'ilike', rec.name),('outsourced_lab_request','=',True)])
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


    @api.model_create_multi
    def create(self, vals_list):
        line_vals = []
        result = super(OutsourcedLabRequest, self).create(vals_list)
        for val in vals_list:
            val['name'] = self.env['ir.sequence'].next_by_code('olrtest_seq')

        return result

    def action_sample_submitted(self):
        self.state = 'sample_submitted'

    def action_reports_received(self):
        self.state = 'reports_received'

    def action_delivered(self):
        self.state = 'delivered'




class OutsourcedLabTestLine(models.Model):
    _name = "outsourced.lab.test.line"
    _description = 'outsourced lab test line'

    medical_test_type_id = fields.Many2one('medical.test_type', 'Test Type', required=True)
    outsourced_lab_test_id = fields.Many2one('outsourced.lab.request', 'Lab Test')