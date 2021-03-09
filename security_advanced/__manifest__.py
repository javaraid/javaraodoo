# -*- coding: utf-8 -*-
{
    'name': "Security Advanced",

    'summary': """
        Advanced security for Javara
    """,

    'description': """
        
    """,

    'author': "Arkana",
    'website': "https://www.arkana.co.id",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Security',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'sale',
        'sales_team',
        'purchase',
        'account',
        'stock',
        'mrp',
        'point_of_sale',
        'web_settings_dashboard',
        'base_setup',
        'security_base',
        'sale_javara',
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/menuitem.xml',
        # 'data/res_users.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}