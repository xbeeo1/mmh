# -*- coding: utf-8 -*-
from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Adds a boolean to enable custom footer and a field to store custom HTML content for POS receipts.
    pos_custom_receipt_footer = fields.Html(string='Receipt Custom Footer',compute='_compute_pos_receipt_custom_footer', inverse='_inverse_pos_custom_receipt_footer',readonly=False, store=True)
    pos_iface_custom_footer = fields.Boolean(related='pos_config_id.is_custom_footer', readonly=False)

    @api.depends('pos_iface_custom_footer', 'pos_config_id')
    def _compute_pos_receipt_custom_footer(self):
        for res_config in self:
            if res_config.pos_iface_custom_footer:
                print('res_config.pos_config_id.receipt_custom_footer',res_config.pos_config_id.receipt_custom_footer)
                res_config.pos_custom_receipt_footer = res_config.pos_config_id.receipt_custom_footer
            else:
                res_config.pos_custom_receipt_footer = False

    def _inverse_pos_custom_receipt_footer(self):
        for rec in self:
            if rec.pos_config_id:
                rec.pos_config_id.receipt_custom_footer = rec.pos_custom_receipt_footer