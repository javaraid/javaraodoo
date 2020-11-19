# -*- coding: utf-8 -*-
{
    'name': "POS No Negative",

    'summary': """
        Prevent negative stock on point of sale
    """,

    'description': """

    """,

    'author': "Arkana",
    'website': "https://www.arkana.co.id",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Inventory',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'stock',
        'point_of_sale',
        'check_available_stock',
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/views.xml',
        # 'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}