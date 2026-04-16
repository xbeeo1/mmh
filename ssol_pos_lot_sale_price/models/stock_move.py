# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from collections import defaultdict

class StockMOveInheritLotwise(models.Model):
    _inherit = 'stock.move'
    _description = 'stock.move.inherit'

    lot_id = fields.Many2one('stock.lot','lot/Batch',domain="[('product_id', '=', product_id)]")



    @api.onchange('lot_id')
    def onchage_lot_id(self):
        if self.lot_id:
            if 'mrp_date' in self._fields:
                self.mrp_date = self.lot_id.mrp_date
            if 'expiration_date' in self._fields:
                self.expiration_date = self.lot_id.expiration_date
            if 'shelf_life' in self._fields:
                self.shelf_life = self.lot_id.shelf_life

    @api.onchange('product_id')
    def onchage_product_id(self):
        if self.picking_code != 'internal':
            if 'batch_name' in self._fields:
                if self.batch_name:
                    lot_obj = self.env['stock.lot'].search([('name','=',self.batch_name)])
                    if lot_obj:
                        self.lot_id = lot_obj.id





