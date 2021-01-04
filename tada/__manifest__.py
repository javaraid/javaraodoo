{'name': 'Tada Integration',
'summary': 'Integrates customer, product, and order.',
'version': '1.0',
'author': 'Arkana Teknologi',
'website': 'https://arkanateknologi.co.id',
'category': 'Sales',
'depends': ['sale_stock', 'web_widget_image_url'],
'data': ['security/ir.model.access.csv',
         'data/tada_data.xml',
         'wizard/tada_authenticate_wizard.xml',
         'views/tada_views.xml',
         'views/tada_store_views.xml',
         'views/tada_product_views.xml',
         'views/tada_order_views.xml',
         'views/menu.xml'
         ]
}