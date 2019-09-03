{
    'name': 'Kota',
    'description': 'Digunakan untuk menambah pilihan kota pada Odoo',
    'author': 'Arkana, Erlangga Indra Permana',
    'website': 'https://www.arkana.co.id',
    'depends': ['base'],
    'data': [
        'ir.model.access.csv',
        'city_view.xml',
        'res_view.xml',
    ],
    'uninstall_hook': 'uninstall_hook',
    'post_init_hook': 'post_init_hook',
}
