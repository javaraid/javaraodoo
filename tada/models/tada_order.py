from odoo import models, fields, api


class TadaOrder(models.Model):
    _name = 'tada.order'
    _description = 'Order in Tada'
    
    tada_id = fields.Many2one(_name, 'Tada Account', ondelete='cascade')
    name = fields.Char('Order Number') # name
    orderid = fields.Integer('Order ID') # id
    requester_type = fields.Char() # requesterType
    requesterId = fields.Integer() # requesterId
    order_type = fields.Char() # orderType
    order_number = fields.Char() # orderNumber
    order_reference = None # orderReference
    total = fields.Float() # total
    total_all = fields.Float() # totalAll
    status = fields.Char() # status
    request_delivery_date = fields.Datetime() # requestDeliveryDate
    notes = None # notes
    receiver = None # receiver
    recipient_id = fields.Many2one('res.partner', 'Partner') # RecipientId
    internal_reference = fields.Char() # internalReference
    shippingId = None # ShippingId
    storeId = None # storeId
    created_at = fields.Datetime(readonly=True) # createdAt
    updated_at = fields.Datetime(readonly=True) # updatedAt
    order_line_ids = fields.One2many('tada.order.line', 'order_id', 'Tada Order Items') # OrderItems
    fee_line_ids = fields.One2many('tada.fee', 'order_id', 'Tada Order Fees') # Fees
    # SalesOrderDetail
    payment_line_ids = fields.One2many('tada.payment', 'order_id', 'Tada Order Payments')
    

class TadaOrderLine(models.Model):
    _name = 'tada.order.line'
    _description = 'Order Line Tada'
    
    name = fields.Char()
    order_id = fields.Many2one('tada.order', 'Tada Order')
    
    
class TadaFee(models.Model):
    _name = 'tada.fee'
    _description = 'Fee Tada'
    
    name = fields.Char()
    order_id = fields.Many2one('tada.order', 'Tada Order')
    
    
class TadaPayment(models.Model):
    _name = 'tada.payment'
    _description = 'Fee Tada'
    
    order_id = fields.Many2one('tada.order', 'Tada Order')    
    
