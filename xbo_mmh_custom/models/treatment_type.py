# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError


class TreatmentType(models.Model):
    _name = "treatment.type"
    _description = "Treatment Type"

    name = fields.Char(string="Name")
    description = fields.Char(string="Description")

    """CREATE METHOD FOR VALIDATION ON DUPLICATION Village"""
    def create(self, vals):
        if 'name' in vals:
            existing_name = self.search([('name', '=', vals['name'])], limit=1)
            if existing_name:
                raise ValidationError("Treatment Already Exist.")
        return super(TreatmentType, self).create(vals)

