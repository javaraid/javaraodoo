import re
import requests
from odoo.exceptions import ValidationError
from addons.event_sale.models.product import Product
import json
from odoo import models, fields, api, _
from datetime import datetime

StoreUrl = '/v1/integration_merchants/stores'
ShippingCompanyUrl = '/v1/integration_merchants/shipping/companies'
AUTHENTICATION_URL = '/v1/integration_merchants/token'
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
    password = fields.Char(
        string='Password',
        required=True)
    access_token = fields.Char('Token')
    expired_at = fields.Datetime('Expired At', readonly=True)
    state = fields.Selection([('new', 'New'), ('establish', 'Established'), ('expired', 'Expired')], 'State', default='new')
    category_ids = fields.One2many('tada.category', 'tada_id', 'Categories')
    product_ids = fields.One2many('tada.product', 'tada_id', 'Products')
    # mId = fields.Char()
    order_ids = fields.One2many('tada.order', 'tada_id', 'Orders')
    store_ids = fields.One2many('tada.store', 'tada_id', 'Stores')
    # Odoo settings
    warehouse_id = fields.Many2one('stock.warehouse', 'Default Warehouse', required=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id.id)
    product_fee_id = fields.Many2one('product.product', 'Tada Product Fee', required=True)
    
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
        self.check_token_validity()
        Category._get_on_tada(self.access_token)
        Product._get_on_tada(self.access_token)
        Order._get_on_tada(self.access_token)
    
    def act_sync_order(self):
        self = self.with_context(sync=True)
        Order = self.env['tada.order']
        self.check_token_validity()
        Order._get_on_tada(self.access_token)
    
    @sync
    def act_sync_product(self):
        Product = self.env['tada.product']
        self.check_token_validity()
        Product._get_on_tada(self.access_token)
        
    def act_sync_category(self):
        self = self.with_context(sync=True)
        Category = self.env['tada.category']
        self.check_token_validity()
        Category._get_on_tada(self.access_token)
    
    def act_sync_store(self):
        Store = self.env['tada.store'].sudo()
        self.check_token_validity()
        access_token = self.access_token
        base_api_url = self.env['ir.config_parameter'].sudo().get_param('tada.base_api_url')
        authorization = 'Bearer {}'.format(access_token)
        headers = Headers.copy()
        headers['Authorization'] = authorization
        response = requests.get(base_api_url + StoreUrl, headers=headers, timeout=50.0)
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

    @api.multi
    def act_authenticate(self):
        for tada_id in self :
            base_api_url = self.env['ir.config_parameter'].sudo().get_param('tada.base_api_url')
            API_KEY = self.env['ir.config_parameter'].sudo().get_param('tada.api_key')
            API_SECRET = self.env['ir.config_parameter'].sudo().get_param('tada.api_secret')
            body = {'username': tada_id.username, 'password': tada_id.password, "grant_type": "password", "scope": "offline_access"}
            bodyJson = json.dumps(body)
            headers = {'Content-Type': 'application/json'}
            auth_response = requests.post(base_api_url + AUTHENTICATION_URL, auth=(API_KEY, API_SECRET), data=bodyJson, headers=headers)
            if auth_response.status_code != 200:
                raise ValidationError(_('Please check your username or password'))
            resp_json = auth_response.json()
            tada_id.write({'state': 'establish',
                           'access_token': "resp_json['access_token']",
                           'expired_at': resp_json['expired_at']})
        return

    @api.multi
    def check_token_validity(self):
        for rec in self :
            if not rec.access_token or not rec.expired_at or (rec.expired_at and rec.expired_at < datetime.now().strftime('%Y-%m-%d %H:%M:%S')):
                rec.act_authenticate()
        
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
    company_id = fields.Many2one('res.company', 'Company', related='tada_id.company_id')
    

class TadaShippingCompany(models.Model):
    _name = "tada.shipping.company"
    _description = "Tada Shipping Company"
    _rec_name = 'company_name'
    
    shippingCompanyId = fields.Integer('Shipping Company ID')
    brand = fields.Char('Brand Name')
    company_name = fields.Char('Company Name')
    
    @api.model
    def _get_on_tada(self, access_token=False):
        base_api_url = self.env['ir.config_parameter'].sudo().get_param('tada.base_api_url')
        authorization = 'Bearer {}'.format(access_token)
        headers = Headers.copy()
        headers['Authorization'] = authorization
        response = requests.post(base_api_url + ShippingCompanyUrl, timeout=50.0)
        resp_json = response.json()
        if response.status_code != 200 or len(resp_json.get('failed', [])) != 0:
            if 'message' in resp_json:
                message = resp_json['message']
            elif 'failed' in resp_json:
                message = resp_json['failed'][0]['message']
            else:
                message = 'Error'
            raise ValidationError(_(message))
        return
        
        