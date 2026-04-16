

from odoo import models , api ,fields, _


class PosOrderInherit(models.Model):
    _inherit = "pos.order"

    primary_care_physician_id = fields.Many2one('medical.physician', string="Primary Care Doctor")

    @api.model
    def create(self, vals):
        res = super(PosOrderInherit, self).create(vals)
        if 'partner_id' in vals:
            partner = self.env['res.partner'].browse(vals['partner_id'])
            if partner:
                res.primary_care_physician_id = partner.primary_care_physician_id.id
        return res
