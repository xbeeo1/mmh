# -*- coding: utf-8 -*-

from odoo import models

class PosSession(models.Model):
    _inherit = 'pos.session'

    # This function is used to load models into the POS.
    def _load_pos_data_models(self, config_id):
        res = super()._load_pos_data_models(config_id)
        res.append('stock.lot')  # Add custom model name
        return res