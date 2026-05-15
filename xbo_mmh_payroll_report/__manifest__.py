# -*- coding: utf-8 -*-
{
    "name": "Xbo MMH Payroll Report",

    'version': '19.0.0.0',

    'summary': """Xbo MMH Payroll Report""",


    'description': """Xbo MMH Payroll Report""",

    'category': 'Payroll',

    'author': "Xbeeo",

    'website': 'https://xbeeo.com/',

    "depends": ['base','xbo_mmh_payroll_custom'],

    "data": [
        'security/ir.model.access.csv',
        'report/payslip_template.xml',
        'report/employee_pf_template.xml',
        'report/report_action.xml',
        'wizards/employee_payslip_wizard.xml',
        'wizards/employee_pf_report_wizard.xml',
    ],




    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,



}
