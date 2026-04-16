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
        'report/report_action.xml',
        'wizards/multidays_profit_loss_wizard.xml',
        'wizards/pos_profit_loss_wizard_views.xml',
    ],




    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,



}
