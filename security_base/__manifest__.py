# -*- coding: utf-8 -*-
{
    'name': "Base Security",

    'summary': """
        Base security for Javara
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
        'base'
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/res_groups.xml',
        # 'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}