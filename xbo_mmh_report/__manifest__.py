# -*- coding: utf-8 -*-
{
    "name": "Xbo MMH Report",

    'version': '19.0.0.0',

    'summary': """Xbo MMH Report""",

    'description': """Xbo MMH Report""",

    'category': 'MMH',

    'author': "xbeeo",

    'website': 'https://xbeeo.com',

    "depends": ['base','xbo_mmh_custom'],

    "data": [
        'security/ir.model.access.csv',
        'report/multidays_profit_loss_template.xml',
        'report/pos_profit_loss_report_template.xml',
        'report/report_partner_ledger.xml',
        'report/current_balance_report_template.xml',
        'report/discharge_slip_report.xml',
        'report/lab_test_report_template.xml',
        'report/patient_card_report_template.xml',
        'report/sale_summary_report_template.xml',
        'report/report_action.xml',
        'wizards/multidays_profit_loss_wizard.xml',
        'wizards/pos_profit_loss_wizard_views.xml',
        'wizards/customer_balance_wizard_views.xml',
        'wizards/vendor_balance_views.xml',
        'wizards/discharge_slip_wizard_views.xml',
        'wizards/sales_summary_report_wizard_view.xml',

    ],




    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,



}
