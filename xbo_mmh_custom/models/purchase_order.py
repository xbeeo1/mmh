# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError

class PurchaseOrderInherit(models.Model):
    _inherit = 'purchase.order'

    licence_status = fields.Selection(string="Licence Status", selection=[('active', 'Active'), ('expired', 'Expired')],
                                      related='partner_id.licence_status', store=True)

    """CREATE METHOD FOR PURCHASE ORDER ON EXPIRED LICENCE"""

    def create(self, vals):
        if 'partner_id' in vals:
            partner_id = self.env['res.partner'].browse(vals.get('partner_id'))
            if not partner_id.is_renewal:
                # CONDITION: If the partner's licence is expired and the partner is not a renewal, raise an error
                if not partner_id.is_renewal and partner_id.licence_status == 'expired':
                    raise ValidationError("Partner Licence has been Expired, Kindly Renew Your Licence")
        return super(PurchaseOrderInherit, self).create(vals)
