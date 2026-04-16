# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError

class ProductProductInherit(models.Model):
    _inherit = 'product.product'

    is_checkup_fees = fields.Boolean(string="Is Checkup Fees", related='product_tmpl_id.is_checkup_fees', store=True)

    create_mrp_order = fields.Boolean(string="To Create MRP Order",related='product_tmpl_id.create_mrp_order', store=True)
    done_mrp_order = fields.Boolean(string="Done MRP Order",related='product_tmpl_id.done_mrp_order', store=True)

    analytic_account_id = fields.Many2one(comodel_name='account.analytic.account',related='product_tmpl_id.analytic_account_id', store=True)