from odoo import models, fields, api
from odoo.exceptions import ValidationError


class TaxSlabLine(models.Model):
    _name = 'tax.slab.line'
    _description = 'Tax Slab'
    _order = 'min_amount asc'

    name = fields.Char(
        string="Slab",
        compute="_compute_name",
        store=True
    )
    min_amount = fields.Float(string="From Amount", required=True)
    max_amount = fields.Float(string="To Amount", required=True)

    tax_percent = fields.Float(string="Tax %", required=True)
    fixed_tax = fields.Float(string="Fixed Tax", required=True)

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)

        slab_id = self.env.context.get('default_slab_id')

        if slab_id:
            last_line = self.search(
                [('slab_id', '=', slab_id)],
                order='max_amount desc',
                limit=1
            )

            if last_line:
                res['min_amount'] = last_line.max_amount + 1
            else:
                res['min_amount'] = 0

        return res

    @api.constrains('min_amount', 'max_amount')
    def _check_amounts(self):
        for rec in self:
            if rec.min_amount >= rec.max_amount:
                raise ValidationError(
                    "Min amount must be less than max amount."
                )

    @api.depends('min_amount', 'max_amount')
    def _compute_name(self):
        for rec in self:
            rec.name = f"{int(rec.min_amount):,} to {int(rec.max_amount):,}"