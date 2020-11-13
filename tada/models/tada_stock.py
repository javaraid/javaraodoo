from odoo import models, fields, api


StockUrl = '/v1/integration_merchants/manage/inventories/stocks'
StockDetailUrl = '/v1/integration_merchants/manage/inventories/stocks/{stockId}'

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
    def _convert_resp_to_vals(self, resp_dict):
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
    
    