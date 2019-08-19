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
        'sale',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_view.xml',
    ],
    'demo': [],
    'test': [
    ],
    'installable': True,
}