# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero, float_compare

from itertools import groupby
from collections import defaultdict

class StockPicking(models.Model):
    _inherit='stock.picking'







