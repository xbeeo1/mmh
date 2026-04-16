# -*- coding: utf-8 -*-
{
    "name": "Xbo MMH Custom POS Receipt",

    'version': '19.0.0.0',

    'summary': """Xbo MMH Custom POS Receipt""",

    'description': """Xbo MMH Custom POS Receipt""",

    'category': 'POS',

    'author': "SelectaSol",

    'website': 'https://selectasol.com',

    "depends": ['base', 'point_of_sale','xbo_mmh_custom'],

    "data": [
        'views/res_config_setting_view.xml'
    ],

    'assets': {
    'point_of_sale._assets_pos': [
        'xbo_mmh_custom_pos_receipt/static/src/**/*',

            ],
        },


    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,



}



