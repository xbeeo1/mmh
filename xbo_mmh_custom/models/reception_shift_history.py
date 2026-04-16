# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta, date


class ReceptionShiftHistory(models.Model):
    _name = "reception.shift.history"
    _description = "reception shift history"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    user_id = fields.Many2one("res.users", string="User", default=lambda self: self.env.user)
    date = fields.Date(string="Date", tracking=True, default=date.today())
    shift_history_line = fields.One2many("shift.history.line", "shift_history_id", string="Reception Shift History", tracking=True)





class DoctorFeesRateHistory(models.Model):
    _name = "shift.history.line"
    _description = "shift.history.line"

    shift_history_id = fields.Many2one('reception.shift.history', string='Shift History Reference', ondelete='cascade')


    datetime_from = fields.Datetime(string="Date Time From")
    datetime_to = fields.Datetime(string="Date Time To")
    receptionist_id = fields.Many2one("res.partner", string="Receptionist")

    opening_balance = fields.Float(string="Opening Balance", tracking=True, store=True)
    closing_balance = fields.Float(string="Closing Balance", tracking=True, store=True)
    is_readonly = fields.Boolean(string="Is Readonly")


    @api.onchange('closing_balance')
    def _onchange_closing_balance(self):
        if self.opening_balance and self.closing_balance:
            self.is_readonly = True



