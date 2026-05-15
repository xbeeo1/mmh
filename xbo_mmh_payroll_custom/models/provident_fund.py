from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError


class ProvidentFund(models.Model):
    _name = 'provident.fund'
    _description = 'Provident Fund'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(string="PF Name",
                       copy=False, readonly=True, default=lambda s: s.env._('New'))
    creation_date = fields.Date(string='Creation Date',default=fields.Date.today)
    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
        ('cancel','Cancel')
    ], string='Status', default='draft')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    department_id = fields.Many2one('hr.department', string='Department')
    payslip_id = fields.Many2one('hr.payslip', string='Payslip Refernce')
    salary_amount = fields.Float('Salary Amount')
    pf_percentage = fields.Integer(string="PF%")
    employee_contribution = fields.Float('Employee contribution')
    employer_contribution = fields.Float('Employer Contribution')
    total_PF_period = fields.Float('Total PF for the period')
    loan_id = fields.Many2one('hr.loan', string="Loan Ref.",
                              help="Reference to the associated loan.")


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals['name'] == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('provident.fund.seq') or _('New')

        return super().create(vals_list)



