# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountAssetInh(models.Model):
    _inherit = 'account.asset.asset'

    medical_room_id = fields.Many2one(comodel_name='medical.room', string='Room No.', help="Select Room")
    department_id = fields.Many2one(comodel_name='hr.department', string='Department', help="Select Department")
    
