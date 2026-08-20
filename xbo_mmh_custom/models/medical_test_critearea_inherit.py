# -*- coding: utf-8 -*-
from odoo import fields, models

class MedicalTestCritearea(models.Model):
    _inherit = 'medical_test.critearea'

    result_text = fields.Many2one('result.text', string='Result Text')