{
    'name': 'Sale Javara',
    'summary': 'Custom Sale Management for Javara',
    'license': 'AGPL-3',
    'version': '11.0',
    'category': 'Sales',
    'author': 'Arkana, Joenan <joenan@arkana.co.id>',
    'website': 'https://www.arkana.co.id',
    'description': """Custom Sale Management for Javara""",
    'depends': [
        'sale','sale_stock'
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/record_rules.xml',
        'views/sale_view.xml',
        # 'views/_menu_item.xml',
        'report/sale_order_report.xml'
    ],
    'demo': [],
    'test': [
    ],
    'installable': True,
}
