# -*- coding: utf-8 -*-


from odoo import fields, models


class HREmployeeInh(models.Model):
    _inherit = 'hr.employee'

    salary = fields.Float(string='Salary', help='Add Faculty Salary')
    
