import json
import requests
from odoo import models, fields, api


StockUrl = '/v1/integration_merchants/manage/inventories/stocks'
StockDetailUrl = '/v1/integration_merchants/manage/inventories/stocks/{stockId}'
Headers = {'Content-Type': 'application/json', 'Authorization': None}

TadaStockFields = {'name', 'price', 'quantity'}


class TadaStock(models.Model):
    _name = 'tada.stock'
    _description = 'Tada Product Stock'
    
    product_id = fields.Many2one('tada.product', 'Product')
    stockid = fields.Integer() # id
    mId = None # mId
    stock_type = fields.Char() # stockType
    name = fields.Char() # name
    terms = fields.Html() # terms
    price = fields.Integer() # price
    default_exp_type = fields.Char() # defaultExpType
    default_exp = fields.Integer() # defaultExp
    default_exp_date = fields.Date() # defaultExpDate
    is_limited = fields.Boolean() # isLimited
    quantity = fields.Integer() # quantity
    fulfillment_by = None # fulfillmentBy
    availability = None # availability
    image = fields.Char() # image
    weight = fields.Integer() # weight
    length = fields.Integer() # length
    height = fields.Integer() # height
    width = fields.Integer() # width
    active = fields.Boolean() # active
    createdAt = fields.Datetime(readonly=True) # createdAt
    updatedAt = fields.Datetime(readonly=True) # updatedAt
    
    @api.model
    def _convert_resp_tada_to_vals(self, resp_dict):
        stock_type = resp_dict['stockType']
        stockid = resp_dict['id']
        name = resp_dict['name']
        terms = resp_dict['terms']
        price = resp_dict['price']
        default_exp_type = resp_dict['defaultExpType']
        default_exp = resp_dict['defaultExp']
        default_exp_date = resp_dict['defaultExpDate']
        is_limited = resp_dict['isLimited']
        quantity = resp_dict['quantity']
        image = resp_dict['image']
        weight = resp_dict['weight']
        length = resp_dict['length']
        height = resp_dict['height']
        width = resp_dict['width']
        active = resp_dict['active']
        createdAt = resp_dict['createdAt']
        updatedAt = resp_dict['updatedAt']
        stock_vals = {'stockid': stockid,
                      'stock_type': stock_type,
                      'name': name,
                      'terms': terms,
                      'price': price,
                      'default_exp_type': default_exp_type,
                      'default_exp': default_exp,
                      'default_exp_date': default_exp_date,
                      'is_limited': is_limited,
                      'quantity': quantity,
                      'image': image,
                      'weight': weight,
                      'length': length,
                      'height': height,
                      'width': width,
                      'active': active,
                      'createdAt': createdAt,
                      'updatedAt': updatedAt,}
        return stock_vals
    
    @api.model
    def create(self, vals):
        res = super(TadaStock, self).create(vals)
        if not self._context.get('sync', False):
            res._create_to_tada(vals)
        return res
    
    def write(self, vals):
        res = super(TadaStock, self).write(vals)
        if not self._context.get('sync', False):
            self._update_to_tada(vals)
        return res
    
    def _create_to_tada(self, vals):
        access_token = self.product_id.tada_id.access_token
        base_api_url = self.env['ir.config_parameter'].sudo().get_param('tada.base_api_url')
        authorization = 'Bearer {}'.format(access_token)
        headers = Headers.copy()
        headers['Authorization'] = authorization
        body = {"name": vals.get('name'),
                "quantity": vals.get('quantity', 0),
                "price": vals.get('price', 0),
                "availability": [
                  "redemption"
                 ]
                }
        response = requests.post(base_api_url + StockUrl, headers=headers, json=body, timeout=10.0)
        resp_json = response.json()
        resp_vals = self._convert_resp_tada_to_vals(resp_json)
        return self.with_context(sync=True).write(resp_vals)
    
    def _update_to_tada(self, vals):
        updated_fields = set(vals.keys())
        difference_field = updated_fields.difference(TadaStockFields)
        for field in difference_field:
            vals.pop(field)
        if len(vals) == 0:
            return
        body = {'name': vals.get('name', self.name), 'price': vals.get('price', self.price), 'quantity': vals.get('quantity', self.quantity)}
        bodyJson = json.dumps(body)
        base_api_url = self.env['ir.config_parameter'].sudo().get_param('tada.base_api_url')
        access_token = self.product_id.tada_id.access_token
        authorization = 'Bearer {}'.format(access_token)
        headers = Headers.copy()
        headers['Authorization'] = authorization
        response = requests.put(base_api_url + StockDetailUrl.format(stockId=self.stockid), headers=headers, data=bodyJson, timeout=10.0)
        resp_json = response.json()
        if response.status_code != 200:
            raise ValidationError(_('Request cannot be completed'))
        self.with_context(sync=True).write({'updatedAt': resp_json['updatedAt']})
        
        