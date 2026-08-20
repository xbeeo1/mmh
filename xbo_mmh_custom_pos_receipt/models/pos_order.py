# -*- coding: utf-8 -*-

from odoo import api, models, _
from odoo.exceptions import UserError


class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    @api.model
    def get_existing_lots(self, company_id, config_id, product_id):
        self.check_access("read")

        pos_config = self.env["pos.config"].browse(config_id)
        if not pos_config:
            raise UserError(_("No PoS configuration found"))

        src_loc = pos_config.picking_type_id.default_location_src_id

        domain = [
            "|",
            ("company_id", "=", False),
            ("company_id", "=", company_id),
            ("product_id", "=", product_id),
            ("location_id", "in", src_loc.child_internal_location_ids.ids),
            ("quantity", ">", 0),
            ("lot_id", "!=", False),
        ]

        groups = self.sudo().env["stock.quant"]._read_group(
            domain=domain,
            groupby=["lot_id"],
            aggregates=["quantity:sum"],
        )

        result = []

        for lot_recordset, total_quantity in groups:
            if lot_recordset:
                result.append({
                    "id": lot_recordset.id,
                    "name": lot_recordset.name,
                    "product_qty": total_quantity,
                    "expiration_date": lot_recordset.expiration_date.strftime('%d/%m/%Y'),
                })

        return result