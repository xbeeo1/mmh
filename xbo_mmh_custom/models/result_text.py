from odoo import fields, models

class ResultText(models.Model):
    _name = 'result.text'
    _description = 'Result Text'

    name = fields.Char(string='Name', required=True)