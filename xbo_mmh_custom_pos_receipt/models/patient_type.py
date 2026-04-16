# -*- coding: utf-8 -*-

from odoo import models, fields


# Inherit the patient.type model and enable it for POS loading
class PatientType(models.Model):
    _name = 'patient.type'
    _inherit = ['patient.type','pos.load.mixin']


    # This function is used to load fields into the POS.
    def _load_pos_data_fields(self, config_id):
        # Define which fields to send to the POS frontend
        return ['id', 'name']