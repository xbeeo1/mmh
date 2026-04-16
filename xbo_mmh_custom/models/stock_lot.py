# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError


class StockLotInheritEmc(models.Model):
    _inherit = 'stock.lot'
    _description = 'stock.lot.inherit'


    mrp_date = fields.Date(string="Mrp Date", compute='_compute_is_stock_move', store=True)
    shelf_life = fields.Float(string="Shelf Life (%)", compute='_compute_is_stock_move', store=True)
    is_stock_move = fields.Boolean(string="Is Stock Move", compute='_compute_is_stock_move')
    notification_date = fields.Date(string="Notification Date", default=date.today())
    today_test_date = fields.Date(string="Today Test Date")

    active = fields.Boolean(string="Archived", default=True)
    sale_price = fields.Float('Sale Price')



    """GET RELATED MRP DATE AND SHELF LIFE FROM STOCK MOVE"""

    @api.depends('is_stock_move', 'mrp_date', 'shelf_life')
    def _compute_is_stock_move(self):
        for rec in self:
            move_lines = self.env['stock.move.line'].search([('lot_id', '=', rec.id)], limit=1)

            # print("Related Lot in Stock Move line:", move_lines.lot_name)
            # print("Related Stock Move:", move_lines.move_id.reference)

            for line in move_lines:
                rec.mrp_date = line.move_id.mrp_date
                rec.shelf_life = line.move_id.shelf_life

            rec.is_stock_move = False

    """SCHEDULE ACTION FOR PRODUCT EXPIRY NOTIFICATION"""

    def _action_product_expiry_notification(self):

        print('Product Expiry Notification Run Schedule')

        """FETCH VALUES FROM SETTING DATA"""
        setting_data = self.action_get_exp_notification_data()
        exp_notify_bf = setting_data.get('exp_notification_before')
        exp_notify_sc = setting_data.get('exp_notification_schedule')
        exp_notify_users = setting_data.get('user_ids')

        if exp_notify_bf and exp_notify_sc and exp_notify_users:

            print('\n', '\n')

            date_today = date.today()
            lots = self.env['stock.lot'].search([])

            for user in exp_notify_users:  # LOOP ON SELECTED NOTIFY USER

                for lot in lots:

                    if lot.expiration_date:
                        exp_date = lot.expiration_date.date()  # SPLIT EXPIRATION DATE FROM DATETIME

                        """VERIFY NOTIFICATION PERIOD NOTIFICATION DATE AND CREATE ACTIVITY"""
                        self.varify_notification_time_period(lot, exp_notify_bf, exp_notify_sc, exp_date, user)

    """VERIFY NOTIFICATION PERIOD NOTIFICATION DATE AND CREATE ACTIVITY"""

    def varify_notification_time_period(self, lot, exp_notify_bf, exp_notify_sc, exp_date, user):

        toda_date = date.today()
        lot_id = lot
        exp_notify_bf = exp_notify_bf
        exp_notify_sc = exp_notify_sc
        exp_date = exp_date
        user_id = user

        exp_date_7dm = exp_date - relativedelta(days=7)  # 7 days minus
        exp_date_1mm = exp_date - relativedelta(months=1)  # 1 month Minus
        exp_date_3mm = exp_date - relativedelta(months=3)  # 3 month minus
        exp_date_6mm = exp_date - relativedelta(months=6)  # 6 month minus
        exp_date_1ym = exp_date - relativedelta(years=1)  # 1 year minus

        print('exp_notify_bf', exp_notify_bf, 'exp_notify_sc.....', exp_notify_sc)
        print('lot..', lot_id.name, 'exp date', exp_date, user_id.name, 'Today Date....', toda_date)

        if exp_notify_bf == 'week':

            # if toda_date > exp_date_7dm:  # today date 8 jan after minus exp date 7 days it will be 1 jan
            if toda_date >= exp_date_7dm:

                print('Week Period of Notification Start from ', exp_date_7dm)

                if exp_date >= lot_id.notification_date:

                    print('Expiry Date is Greater Than Notification Date', exp_date, '____', lot_id.notification_date)

                    if lot_id.notification_date == toda_date:
                        self.action_create_activity(lot_id, user_id, exp_notify_sc)


        elif exp_notify_bf == 'month':

            if toda_date >= exp_date_1mm:

                print('Month Period of Notification Start from ', exp_date_1mm)

                if exp_date >= lot_id.notification_date:

                    print('Expiry Date is Greater Than Notification Date', exp_date, '____', lot_id.notification_date)

                    if lot_id.notification_date == toda_date:
                        self.action_create_activity(lot_id, user_id, exp_notify_sc)


        elif exp_notify_bf == 'quarter':

            if toda_date >= exp_date_3mm:

                print('Quarter Period of Notification Start from ', exp_date_3mm)

                if exp_date >= lot_id.notification_date:

                    print('Expiry Date is Greater Than Notification Date', exp_date, '____', lot_id.notification_date)

                    if lot_id.notification_date == toda_date:
                        self.action_create_activity(lot_id, user_id, exp_notify_sc)



        elif exp_notify_bf == 'bi_annual':

            if toda_date >= exp_date_6mm:

                print('Bi Annual Period of Notification Start from ', exp_date_6mm)

                if exp_date >= lot_id.notification_date:

                    print('Expiry Date is Greater Than Notification Date', exp_date, '____', lot_id.notification_date)

                    if lot_id.notification_date == toda_date:
                        self.action_create_activity(lot_id, user_id, exp_notify_sc)


        elif exp_notify_bf == 'annual':

            if toda_date >= exp_date_1ym:

                print('Annual Period of Notification Start from ', exp_date_1ym)

                if exp_date >= lot_id.notification_date:

                    print('Expiry Date is Greater Than Notification Date', exp_date, '____', lot_id.notification_date)

                    if lot_id.notification_date == toda_date:
                        self.action_create_activity(lot_id, user_id, exp_notify_sc)

    """CREATE ACTIVITY NOTIFICATION ACTION AND UPDATE NOTIFICATION DATE"""

    def action_create_activity(self, lot_id, user_id, exp_notify_sc):
        print('\n')
        exp_notify_sc = exp_notify_sc
        user_id = user_id
        lot_id = lot_id
        summary = 'Your Product ' + str(lot_id.product_id.name) + ' is going to expire on ' + str(
            lot_id.expiration_date)

        """NOTIFICATION SENDING TO ASSIGNED USERS"""
        if user_id:
            model_id = self.env['ir.model']._get(self._name).id
            activity = ({
                'res_name': lot_id.name,
                'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                'summary': summary,
                'note': 'Product Expiry Notification',
                'automated': True,
                'date_deadline': date.today(),
                'user_id': user_id.id,
                'res_id': lot_id.id,
                'res_model_id': model_id,

            })

            print('activity Data', activity)
            record = self.env['mail.activity'].create(activity)

            # UPDATE ACTIVITY NOTIFICATION ON THE BASE OF NOTIFICATION SCHEDULE
            if record:
                if exp_notify_sc == 'daily':
                    lot_id.notification_date = lot_id.notification_date + relativedelta(days=1)

                elif exp_notify_sc == 'weekly':
                    lot_id.notification_date = lot_id.notification_date + relativedelta(days=7)

                elif exp_notify_sc == 'monthly':
                    lot_id.notification_date = lot_id.notification_date + relativedelta(months=1)

                elif exp_notify_sc == 'quarterly':
                    lot_id.notification_date = lot_id.notification_date + relativedelta(months=3)

                elif exp_notify_sc == 'bi_annually':
                    lot_id.notification_date = lot_id.notification_date + relativedelta(months=6)

                elif exp_notify_sc == 'annually':
                    lot_id.notification_date = lot_id.notification_date + relativedelta(years=1)

                print('Notification Created Successfully', record)

                print('After Schedule', exp_notify_sc, 'Next Notification Date Will Be', lot_id.notification_date)

    """ACTION GET SETTING VALUES FOR EXPIRY NOTIFICATION"""

    def action_get_exp_notification_data(self):
        exp_notification_before = self.env['ir.config_parameter'].sudo().get_param(
            'ssol_emc_customization.exp_notification_before')
        exp_notification_schedule = self.env['ir.config_parameter'].sudo().get_param(
            'ssol_emc_customization.exp_notification_schedule')
        user_ids = self.env['ir.config_parameter'].sudo().get_param('ssol_emc_customization.user_ids')

        # Safely convert the string to a list of integers
        if user_ids:
            user_ids_list = list(map(int, user_ids.strip('[]').split(',')))
        else:
            user_ids_list = []
        subscriptable_user_ids = self.env['res.users'].sudo().browse(user_ids_list).exists()

        setting_data = {
            'exp_notification_before': exp_notification_before,
            'exp_notification_schedule': exp_notification_schedule,
            'user_ids': subscriptable_user_ids,
        }

        print('setting_data', setting_data)

        return setting_data








