# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import calendar
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    partner_mobile = fields.Char(string="Mobile", related='partner_id.phone', store=True)
    department_id = fields.Many2one("hr.department", string="Department")
    patient_type_id = fields.Many2one("patient.type", string="Patient Type")
    doctor_id = fields.Many2one("res.partner", string="Doctor")
    employee_id = fields.Many2one("hr.employee", string="Invoice Created By")
    outsourced_lab_request = fields.Boolean(string="Outsourced Lab Request")

    licence_status = fields.Selection(string="Licence Status", selection=[('active', 'Active'), ('expired', 'Expired')],
                                      related='partner_id.licence_status', store=True)

    """CREATE METHOD FOR BILL VALIDATION ON EXPIRED LICENCE"""

    def create(self, vals):
        if 'move_type' in vals and 'partner_id' in vals:
            partner_id = self.env['res.partner'].browse(vals.get('partner_id'))
            # CONDITION: If the partner's licence is expired and the partner is not a renewal, raise an error
            if not partner_id.is_renewal and partner_id.licence_status == 'expired':
                raise ValidationError("Partner Licence has been Expired, Kindly Renew Your Licence")
        return super(AccountMoveInherit, self).create(vals)

        # """DUPLICATE METHOD FOR BILL VALIDATION ON EXPIRED LICENCE"""

        def _licence_validity_notification(self):

            partners = self.env['res.partner'].search([])
            today_date = date.today()
            # Loop through all partners
            for partner in partners:  # Assuming 'partners' is a list of partner objects
                if partner.licence_validity_date:
                    date_validity = partner.licence_validity_date

                    date_validity_minus_one_month = date_validity - relativedelta(months=1)

                    # print('partner:', partner.name, 'date_validity:', date_validity, 'date_validity_minus_one_month:', date_validity_minus_one_month)

                    # CONDITION: If today's date is past the licence validity date minus one month, create an activity
                    if today_date > date_validity_minus_one_month:
                        # print('create activity', 'test_date:', today_date, 'date_validity_minus_one_month:', date_validity_minus_one_month)
                        expiry_date = date_validity
                        contact = partner  # Assuming 'self' refers to the current account move or context
                        self.action_create_activity(contact, expiry_date)

        def action_create_activity(self, contact, expiry_date):

            contact = contact
            expiry_date = expiry_date
            summary = 'Your Licences is going to expire on ' + str(expiry_date)
            setting_data = self.action_get_exp_notification_data()
            exp_notify_users = setting_data.get('user_ids')

            """NOTIFICATION SENDING TO MULTIPLE ASSIGNED USERS"""
            for user_id in exp_notify_users:
                if user_id:
                    # print('run schedule.............on Contact : ', contact.name, 'For User', user_id.name)

                    model_id = self.env['ir.model']._get('res.partner').id

                    print('res_id', contact.name)
                    activity = ({
                        'res_name': contact.name,
                        'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                        'summary': summary,
                        'note': 'Notification For Licence Expiry Date Arrival',
                        'automated': True,
                        'date_deadline': date.today(),
                        'user_id': user_id.id,
                        'res_id': contact.id,
                        'res_model_id': model_id,

                    })
                    activities = self.env['mail.activity'].create(activity)
                    # print('activities..................', activities, '\n')

        """ACTION GET SETTING VALUES FOR EXPIRY NOTIFICATION"""

        def action_get_exp_notification_data(self):
            user_ids = self.env['ir.config_parameter'].sudo().get_param('ssol_emc_customization.user_ids')

            # Safely convert the string to a list of integers
            if user_ids:
                user_ids_list = list(map(int, user_ids.strip('[]').split(',')))
            else:
                user_ids_list = []
            subscriptable_user_ids = self.env['res.users'].sudo().browse(user_ids_list).exists()

            setting_data = {
                'user_ids': subscriptable_user_ids,
            }

            return setting_data

        """WRITE METHOD FOR BILL VALIDATION ON EXPIRED LICENCE"""

        def write(self, vals):
            if 'move_type' in vals and 'partner_id' in vals:
                move_type = vals.get('move_type')
                partner_id = self.env['res.partner'].browse(vals.get('partner_id'))
                if move_type == 'in_invoice' and not partner_id.is_renewal:
                    date_validity = partner_id.licence_validity_date
                    today_date = date.today()
                    print('partner is:', partner_id.name, 'date_validity:', date_validity, 'Today Date:', today_date)

                    # Subtract one month from the licence validity date
                    date_validity_minus_one_month = date_validity - relativedelta(months=1)

                    # CONDITION: If today's date is past the licence validity date minus one month, create an activity
                    if today_date > date_validity_minus_one_month:
                        print('create activity', 'test_date:', today_date, 'date_validity_minus_one_month:',
                              date_validity_minus_one_month)

                    # Debug output to verify dates
                    print('test_date:', today_date, 'date_validity:', date_validity)

                    # CONDITION: If today's date is greater than or equal to the licence validity date, raise an error
                    if today_date >= date_validity:
                        raise ValidationError(
                            'Partner Licence (' + str(date_validity) + ') has been Expired, Kindly Renew Your Licence')

                    # CONDITION: If the partner's licence is expired and the partner is not a renewal, raise an error
                    if not partner_id.is_renewal and partner_id.licence_status == 'expired':
                        raise ValidationError("Partner Licence has been Expired, Kindly Renew Your Licence")

            return super(AccountMoveInheritEmc, self).write(vals)


