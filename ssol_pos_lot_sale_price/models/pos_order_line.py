# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    @api.model
    def create(self, vals_list):
        if 'refunded_orderline_id' in vals_list:
            refunded_id = vals_list['refunded_orderline_id']
            if refunded_id and not vals_list['pack_lot_ids']:
                refunded_line = self.env['pos.order.line'].browse(refunded_id)
                if refunded_line and refunded_line.pack_lot_ids:
                    vals_list["pack_lot_ids"] = [
                        (0, 0, {
                            "lot_name": lot.lot_name,
                            "id": lot.id,
                        }) for lot in refunded_line.pack_lot_ids
                    ]
        return super().create(vals_list)

