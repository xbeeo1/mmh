from odoo import models, fields

class DischargeSlipWizard(models.TransientModel):
    _name = 'discharge.slip.wizard'
    _description = 'Discharge Slip Wizard'

    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)
    patient_id = fields.Many2one('medical.patient', required=True)

    def action_print_report(self):
        return self.env.ref('xbo_mmh_custom.action_discharge_slip_report').report_action(self)

    def _get_field(self, field_name):
        """Check medical.patient first, then fallback to res.partner."""
        patient = self.patient_id
        partner = self.patient_id.patient_id

        if field_name in patient._fields:
            record = patient
        elif field_name in partner._fields:
            record = partner
        else:
            return ''

        value = getattr(record, field_name, False)

        if not value:
            return ''

        field = record._fields[field_name]

        if field.type == 'selection':
            return dict(field._description_selection(record.env)).get(value, value)

        return value