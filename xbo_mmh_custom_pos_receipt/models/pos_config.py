# -*- coding: utf-8 -*-

from odoo import api, fields, models

class PosConfig(models.Model):
    _inherit = 'pos.config'

    # Add option to enable and define a custom HTML footer for POS receipts.
    is_custom_footer = fields.Boolean("Custom Footer")
    receipt_custom_footer = fields.Html(string='Custom Footer')