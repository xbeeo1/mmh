# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from odoo.exceptions import UserError


class MedicalRoom(models.Model):
    _name = 'medical.room'
    _description = 'Medical Room'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', help='Room Name')
    
