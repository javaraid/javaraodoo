import re
import requests
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from addons.event_sale.models.product import Product

StoreUrl = '/v1/integration_merchants/stores'
Headers = {'Content-Type': 'application/json', 'Authorization': None}

def sync(fun):
    def wrapper(par):
        par = par.with_context(sync=True)
        return fun(par)
    return wrapper


class TadaTada(models.Model):
    _name = 'tada.tada'
    _description = 'Tada Account'
    _rec_name = 'username'
    
    name = fields.Char('Name')
    username = fields.Char('Username', required=True)
    access_token = fields.Char('Token')
    expired_at = fields.Datetime('Expired At', readonly=True)
    state = fields.Selection([('new', 'New'), ('establish', 'Established'), ('expired', 'Expired')], 'State', default='new')
    category_ids = fields.One2many('tada.category', 'tada_id', 'Categories')
    product_ids = fields.One2many('tada.product', 'tada_id', 'Products')
    # mId = fields.Char()
    order_ids = fields.One2many('tada.order', 'tada_id', 'Orders')
    
    # Odoo settings
    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse', required=True)
    
    @api.constrains('username')
    def _check_username(self):
        regex = r'[\w.-]+@[\w.-]+.\w+'
        if not re.search(regex,self.username):  
            raise ValidationError("Invalid Email")
    
    @api.model
    def _sync(self):
        tada_ids = self.search([('state', '=', 'establish')])
        for tada_id in tada_ids:
            tada_id.act_sync()
    
    def act_sync(self):
        self = self.with_context(sync=True)
        Category = self.env['tada.category']
        Product = self.env['tada.product']
        Order = self.env['tada.order']
        Category._get_on_tada(self.access_token)
        Product._get_on_tada(self.access_token)
        Order._get_on_tada(self.access_token)
    
    def act_sync_order(self):
        self = self.with_context(sync=True)
        Order = self.env['tada.order']
        Order._get_on_tada(self.access_token)
    
    @sync
    def act_sync_product(self):
        Product = self.env['tada.product']
        Product._get_on_tada(self.access_token)
        
    def act_sync_category(self):
        self = self.with_context(sync=True)
        Category = self.env['tada.category']
        Category._get_on_tada(self.access_token)
    
    def act_sync_store(self):
        Store = self.env['tada.store'].sudo()
        access_token = self.access_token
        base_api_url = self.env['ir.config_parameter'].sudo().get_param('tada.base_api_url')
        authorization = 'Bearer {}'.format(access_token)
        headers = Headers.copy()
        headers['Authorization'] = authorization
        response = requests.get(base_api_url + StoreUrl, headers=headers, timeout=10.0)
        resp_json = response.json()
        store_ids = Store.search([('tada_id', '=', self.id),'|', ('active', '=', True), ('active', '=', False)])
        for store in resp_json:
            storeId = store['id']
            sId = store['sId']
            name = store['location']
            phone = store['phone']
            email = store['email']
            coordinate = store['coordinate']
            address = store['address']
            active = store['active']
            store_type = store['storeType']
            store_vals = {'storeId': storeId,
                    'sId': sId,
                    'name': name,
                    'phone': phone,
                    'email': email,
                    'coordinate': coordinate,
                    'address': address,
                    'active': active,
                    'store_type': store_type,
                    'tada_id': self.id}
            store_id = store_ids.filtered(lambda rec: rec.storeId == storeId)
            if store_id:
                store_id.write.create(store_vals)
            else:
                Store.create(store_vals)
        return
        
        
class TadaStore(models.Model):
    _name = 'tada.store'
    _description = 'Tada Store'
    
    storeId = fields.Integer() # id
    sId = fields.Char() # sId
    name = fields.Char() # location
    contact = None # contact
    contactPosition = None # contactPosition
    phone = fields.Char() # phone
    email = fields.Char() # email
    coordinate = fields.Char() # coordinate
    address = fields.Char() # address
    active = fields.Boolean() # active
    store_type = fields.Char() # storeType
    storeCode = None # storeCode
    bankName = None # bankName
    bankAccountNumber = None # bankAccountNumber
    bankAccountHolder = None # bankAccountHolder
    npwp = None # npwp
    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse')
    tada_id = fields.Many2one('tada.tada', 'Tada', ondelete='cascade')    
    
    