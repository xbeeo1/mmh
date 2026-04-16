# -*- coding: utf-8 -*-
{
    "name": "SSOL POS LOT SALE PRICE",

    'version': '19.0.0.0',

    'summary': """SSOL POS LOT SALE PRICE""",

    'description': """SSOL POS LOT SALE PRICE""",

    'category': 'Point of sale',

    'author': "Musadiq Fiaz",

    'website': 'https://musadiqfiaz.com',

    "depends": ['base','stock','point_of_sale'],

    "data": [
        'views/stock_lot_view.xml',
        'views/stock_picking_view.xml',
    ],

    'assets': {
            'point_of_sale._assets_pos': [
                'ssol_pos_lot_sale_price/static/src/**/*',

                    ],
    },

    'license': 'LGPL-3',
}

