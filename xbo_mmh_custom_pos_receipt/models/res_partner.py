# -*- coding: utf-8 -*-

from odoo import models

class ResPartner(models.Model):
    _inherit = 'res.partner'

    # This function is used to add the custom 'patient_type_id' field from res.partner for use in the POS
    def _load_pos_data_fields(self, config_id):
        fields = super()._load_pos_data_fields(config_id)
        fields += [
            "patient_type_id",
            "mr_number",
        ]
        return fields

