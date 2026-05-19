# -*- coding: utf-8 -*-

from odoo import models, fields

class AccountPaymentInherit(models.Model):
    _inherit = "account.payment"

    description = fields.Char(string="Description")

    def _prepare_move_line_default_vals(self, write_off_line_vals=None, force_balance=None):

        res = super()._prepare_move_line_default_vals(
            write_off_line_vals=write_off_line_vals,
            force_balance=force_balance
        )

        for line_vals in res:
            line_vals.update({
                'description': self.description,
            })

        return res