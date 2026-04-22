from odoo import models , api ,fields, _
from odoo.exceptions import ValidationError
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from odoo.osv import expression
import re


class ResPartnerInherit(models.Model):
    _inherit = "res.partner"

    treatment_type_id = fields.Many2one("treatment.type", string="Treatment Type")
    patient_type_id = fields.Many2one("patient.type", string="Contact/Patient Type")
    department_id = fields.Many2one("hr.department", string="Department")
    village_id = fields.Many2one("patient.village", string="Village")
    patient_cnic = fields.Char(string="CNIC", required=True)
    father_name = fields.Char(string="Father Name")
    sex = fields.Selection([('m', 'Male'), ('f', 'Female')], string="Sex")
    marital_status = fields.Selection([('s', 'Single'),
                                       ('m', 'Married'),
                                       ('w', 'Widowed'),
                                       ('d', 'Divorced'),
                                       ('x', 'Seperated')], string='Marital Status')

    primary_care_physician_id = fields.Many2one('medical.physician', string="Primary Care Doctor")

    sector_type = fields.Selection(string="Sector Type", selection=[('private', 'Private'), ('govt', 'Govt')])
    licence_number = fields.Char(string="Licence Number")
    licence_validity_date = fields.Date(string="Licence Validity Date")
    licence_status = fields.Selection(string="Licence Status", selection=[('active', 'Active'), ('expired', 'Expired')])
    is_renewal = fields.Boolean(string="Is Renewal")

    """CREATE METHOD FOR VALIDATION ON DUPLICATION CNIC"""
    def create(self, vals):
        if isinstance(vals, list):
            for val in vals:
                sector_type = val.get('sector_type')
        else:
            sector_type = vals.get('sector_type')
        if sector_type and sector_type == 'private':
            if 'licence_number' in vals:
                ex_licence_number = self.search([('licence_number', '=', vals['licence_number'])], limit=1)
                if ex_licence_number:
                    raise ValidationError("A customer with this Licence already Exist.")

        if 'patient_cnic' in vals and vals.get('patient_cnic'):
            existing_name = self.search([('patient_cnic', '=', vals['patient_cnic'])], limit=1)
            if existing_name:
                raise ValidationError("Patient CINC Already Exist.")

        if 'patient_type_id' in vals and vals.get('patient_type_id'):
            patient_type = self.env['patient.type'].browse(
                vals['patient_type_id'])  # Replace `patient.type` with the correct model
            patient_type_code = patient_type.code
            print('Patient Type Code:', patient_type_code)

            if patient_type_code and vals.get('name'):
                name  = vals['name']
                vals['name'] = str(patient_type_code) + '-' + str(name)
                # vals['name'] = f"{vals['name']}-{patient_type_code}"

        return super(ResPartnerInherit, self).create(vals)

    @api.constrains('patient_cnic')
    def _check_cnic(self):
        for rec in self:
            if rec.patient_cnic:
                # CNIC format: 15 digits
                if not re.fullmatch(r'\d{5}-\d{7}-\d', rec.patient_cnic):
                    raise ValidationError("CNIC format should be xxxxx-xxxxxxx-x")


    def _licence_status_expire(self):
        partners = self.env['res.partner'].search([])
        today_date = date.today()
        for partner in partners:
            if partner.licence_validity_date == today_date:
                partner.licence_status = 'expired'


    @api.onchange('licence_validity_date')
    def _onchange_licence_validity_date(self):
        print('licence_validity_date', self.licence_validity_date)
        if self.licence_validity_date:
            today = date.today()

            if self.licence_validity_date > today:
                self.licence_status = 'active'
            else:
                self.licence_status = 'expired'

    def write(self, vals):
        if 'licence_number' in vals and vals['licence_number']:  # Ensure 'licence_number' is not empty
            existing_partner = self.search([
                ('licence_number', '=', vals['licence_number']), ('id', '!=', self.id)], limit=1)
            if existing_partner:
                raise ValidationError("A customer with this Licence already exists.")


        return super(ResPartnerInherit, self).write(vals)