from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ReportSignatory(models.Model):
    _name = 'report.signatory'
    _description = 'Report Signatory'
    _order = 'sequence asc'

    name = fields.Char(required=True)
    description = fields.Char()
    sequence = fields.Integer(default=0, readonly=True)
   
    @api.model_create_multi
    def create(self, vals_list):
        # Restrict to only 3 records
        if self.search_count([]) + len(vals_list) > 3:
            raise ValidationError("You can only create 3 signatories.")

        # Auto sequence
        last = self.search([], order='sequence desc', limit=1)
        last_seq = last.sequence if last else 0
        for vals in vals_list:
            last_seq += 1
            vals['sequence'] = last_seq

        return super().create(vals_list)