# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError


class PatientType(models.Model):
    _name = "patient.type"
    _description = "Patient Type"

    name = fields.Char(string="Name")
    code = fields.Char(string="Code")
    description = fields.Char(string="Description")


    """CREATE METHOD FOR VALIDATION ON DUPLICATION Village"""
    def create(self, vals):
        if 'name' in vals:
            existing_name = self.search([('name', '=', vals['name'])], limit=1)
            if existing_name:
                raise ValidationError("Patient Type Already Exist.")
        return super(PatientType, self).create(vals)
