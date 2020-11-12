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
    
    
    
    