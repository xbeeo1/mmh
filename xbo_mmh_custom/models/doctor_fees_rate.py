# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta, date


class DoctorFeesRate(models.Model):
    _name = "doctor.fees.rate"
    _description = "Doctor Fees"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    partner_id = fields.Many2one("res.partner", string="Doctor", tracking=True)
    fee_rate = fields.Float(string="Fees Rate", tracking=True)

    doctor_fees_history_line = fields.One2many("doctor.fees.history", "doctor_fee_id", string="Doctor Fees History", tracking=True)

    """CREATE METHOD FOR VALIDATION ON DUPLICATION Village"""

    def create(self, vals):
        if 'partner_id' in vals and 'fee_rate' in vals:
            fees_history = [(0, 0, {
                'partner_id': vals.get('partner_id'),
                'fee_rate': vals.get('fee_rate'),
                'date': date.today(),
            })]
            vals['doctor_fees_history_line'] = fees_history

        return super(DoctorFeesRate, self).create(vals)


    def write(self, vals):
        # Prepare history line if partner_id or fee_rate is updated
        if 'partner_id' in vals or 'fee_rate' in vals:
            for record in self:
                # Get the updated values or fallback to the current ones
                partner_id = vals.get('partner_id', record.partner_id.id)
                fee_rate = vals.get('fee_rate', record.fee_rate)

                # Add a new history line
                history_line = {
                    'partner_id': partner_id,
                    'fee_rate': fee_rate,
                    'date': date.today(),
                }
                record.doctor_fees_history_line = [(0, 0, history_line)]

        return super(DoctorFeesRate, self).write(vals)




class DoctorFeesRateHistory(models.Model):
    _name = "doctor.fees.history"
    _description = "Doctor Fees History"

    doctor_fee_id = fields.Many2one('doctor.fees.rate', string='Doctor Fee Reference', ondelete='cascade')

    partner_id = fields.Many2one("res.partner", string="Doctor")
    date = fields.Date(string="Date")
    fee_rate = fields.Float(string="Fees Rate")

