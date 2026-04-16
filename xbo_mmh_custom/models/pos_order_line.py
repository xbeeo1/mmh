from odoo import models , api ,fields, _
from odoo.exceptions import ValidationError
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from odoo.osv import expression



class PosOrderLineInherit(models.Model):
    _inherit = "pos.order.line"

    session_id = fields.Many2one("pos.session", string="Session", related='order_id.session_id', store=True)
    user_id = fields.Many2one("res.users", string="Cashier", related='order_id.user_id', store=True)
    partner_id = fields.Many2one("res.partner", string="Customer", related='order_id.partner_id', store=True)
    cost_price = fields.Float(string="Cost Price",related='product_id.lst_price', store=True)
