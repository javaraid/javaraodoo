# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Account Javara',
    'summary': 'Custom Accounting for Javara',
    'license': 'AGPL-3',
    'version': '11.0',
    'category': 'Accounting',
    'author': 'Arkana, Joenan <joenan@arkana.co.id>',
    'website': 'https://www.arkana.co.id',
    'description': """Custom Accounting for Javara""",
    'depends': [
        'account_reports',
        'sale',
        'pos_sale',
        'account_cancel',
    ],
    'data': [
        'wizard/view_aged_partner_wizard.xml',
        'views/account_view.xml'
    ],
    'demo': [],
    'test': [
    ],
    'installable': True,
}
