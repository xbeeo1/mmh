from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class HrLeaveAllocation(models.Model):
    _inherit = 'hr.leave.allocation'

    @api.constrains('employee_id')
    def _check_employee(self):
        for rec in self:
            if rec.employee_id:
                if rec.employee_id.contract_type_id.name != 'Permanent':
                    raise ValidationError("Leave Allocation only for Permanent Employee")
                if rec.holiday_status_id.work_entry_type_id.code == 'LEAVE160' and rec.number_of_days > 10:
                    raise ValidationError("Yor are not allowed to allocate more then 10 Special Leaves.")