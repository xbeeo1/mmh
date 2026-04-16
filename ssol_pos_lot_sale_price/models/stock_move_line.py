# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta

class StockMOveLineInheritLotwise(models.Model):
    _inherit = 'stock.move.line'
    _description = 'stock.move.line.inherit'




    @api.model
    def create(self, values):
        print(values)
        if 'move_id' in values:
            move = self.env['stock.move'].search([('id','=',values['move_id'])])
            ctx = self.env.context
            act_id = ctx.get("config_id")

            if act_id and 'quant_id' not in values and 'lot_id' not in values and 'lot_name' not in values:
                if move.has_tracking != 'none':
                    return self.browse()
            if move.picking_code == 'internal':
                values['lot_id'] = move.lot_id.id
        return super(StockMOveLineInheritLotwise, self).create(values)

    def write(self, vals):
        if 'quant_id' in vals:
            if self.picking_type_id.code == 'outgoing' and self.picking_type_id.sequence_code:
                quant = self.env['stock.quant'].search([('id','=',vals['quant_id'])])
                vals['expiration_date'] = quant.lot_id.expiration_date
        return super(StockMOveLineInheritLotwise, self).write(vals)

