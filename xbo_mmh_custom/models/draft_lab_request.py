# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import date,datetime

class MedicalPatientLabTest(models.Model):
    _inherit = "medical.patient.lab.test"
    _description = 'medical Prescription order Inherit'
    _rec_name = 'patient_id_name'

    patient_id_name = fields.Char(string="Patient ID")
    medical_test_type_id = fields.Many2one('medical.test_type', 'Test Type', required=False)

    lab_test_lines = fields.One2many('medical.patient.lab.test.line', 'lab_test_id',
                                 string="Lab Test Line")

    outsourced_lab_request = fields.Boolean(string="Outsourced Lab Request")

    partner_lab_id = fields.Many2one(comodel_name='partner.lab', string="Partner Lab")




    @api.onchange('patient_id_name')
    def _onchange_patient_id_name(self):
        if self.patient_id_name and not self.patient_id:
            patient = self.env['medical.patient'].search([('name', '=', self.patient_id_name)], limit=1)
            patient_mobile = self.env['medical.patient'].search([('patient_mobile', '=', self.patient_id_name)], limit=1)
            if patient:
                self.patient_id = patient.id
            elif patient_mobile:
                self.patient_id = patient_mobile.id



    @api.onchange('patient_id')
    def _onchange_patient_id(self):
        print('self.patient_id', self.patient_id.name)
        if not self.patient_id_name and self.patient_id:
            self.patient_id_name = self.patient_id.name


class MedicalPatientLabTestLine(models.Model):
    _name = "medical.patient.lab.test.line"
    _description = 'medical Prescription order line'

    medical_test_type_id = fields.Many2one('medical.test_type', 'Test Type', required=True)
    lab_test_id = fields.Many2one('medical.patient.lab.test', 'Lab Test')
