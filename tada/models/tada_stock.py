from odoo import models, fields, api


StockUrl = '/v1/integration_merchants/manage/inventories/stocks'


class TadaStock(models.Model):
    _name = 'tada.stock'
    _description = 'Tada Product Stock'
    
    tada_product_id = fields.Many2one('tada.product', 'Product')
    tadaId = fields.Integer() # id
    mId = None # mId
    stockType = fields.Char() # stockType
    name = fields.Char() # name
    terms = fields.Html() # terms
    price = fields.Integer() # price
    defaultExpType = fields.Char() # defaultExpType
    defaultExp = fields.Integer() # defaultExp
    defaultExpDate = fields.Date() # defaultExpDate
    isLimited = fields.Boolean() # isLimited
    quantity = fields.Integer() # quantity
    fulfillmentBy = None # fulfillmentBy
    availability = None # availability
    image = fields.Char() # image
    weight = fields.Integer() # weight
    length = fields.Integer() # length
    height = fields.Integer() # height
    width = fields.Integer() # width
    active = fields.Boolean() # active
    createdAt = fields.Datetime(readonly=True) # createdAt
    updatedAt = fields.Datetime(readonly=True) # updatedAt
    
    