# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta

class StockMOveInherit(models.Model):
    _inherit = 'stock.move'
    _description = 'stock.move.inherit'

    batch_name = fields.Char(string="Batch Name", related='move_line_ids.lot_id.name', store=True)
    expiration_date = fields.Datetime(string="Expiration Date", related='move_line_ids.expiration_date', store=True)
    mrp_date = fields.Date(string="MFG Date", readonly= False)
    # mrp_date = fields.Date(string="MFG Date", readonly= False)

    shelf_type = fields.Selection(string="Shelf Life", selection=[('with_shelf_life', 'With Shelf Life'),
                                                                  ('without_shelf_life', 'Without Shelf Life')],
                                  default='without_shelf_life')
    shelf_life = fields.Float(string="Shelf Life (%)", compute='_compute_shelf_life')



    @api.constrains('expiration_date', 'picking_id')
    def _check_expiration_date_gap(self):
        for move in self:
            if move.expiration_date and move.picking_id.scheduled_date and move.expiration_date != move.picking_id.scheduled_date:

                if move.expiration_date < move.picking_id.scheduled_date + relativedelta(months=6):
                    raise ValidationError(_(
                        "Expiration Date must be at least 6 months after Scheduled Date."
                    ))


    """COMPUTE SHELF LIFE"""
    @api.depends('mrp_date', 'shelf_life', 'move_line_ids.expiration_date')
    def _compute_shelf_life(self):
        for rec in self:

            move_length = len(rec.move_line_ids)

            if move_length <= 1:
                if rec.move_line_ids.lot_id.mrp_date:
                    rec.mrp_date= rec.move_line_ids.lot_id.mrp_date
                if rec.move_line_ids.expiration_date and rec.mrp_date:

                    date_today = date.today()
                    exp_date_only = rec.move_line_ids.expiration_date.date()
                    # print('exp_date_only', exp_date_only, 'date_today', date_today)

                    # Calculate the result
                    if rec.mrp_date < exp_date_only:  # Ensure valid date range to avoid ZeroDivisionError
                        date1 = (exp_date_only - date_today).days
                        date2 = (exp_date_only - rec.mrp_date).days

                        date3 = (date1 / date2) * 100
                        rec.shelf_life = date3
                        # print('Result:', date1, date2, date3)
                    else:
                        rec.shelf_life = False
                        # raise ValidationError('Invalid dates :' 'Mrp Date ', rec.mrp_date, 'should be before Expiration date', rec.expiry_date_product)

                else:
                    rec.shelf_life = False

            else:
                rec.shelf_life = False








