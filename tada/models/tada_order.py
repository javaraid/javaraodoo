import json
import requests
from odoo import models, fields, api


OrderUrl = '/v1/integration_merchants/manage/orders'
OrderDetailUrl = '/v1/integration_merchants/manage/orders/detail/{orderNumberOrId}'


class TadaOrder(models.Model):
    _name = 'tada.order'
    _description = 'Order in Tada'
    _rec_name = 'order_number'
    
    tada_id = fields.Many2one('tada.tada', 'Tada Account', ondelete='cascade', required=True, index=True)
    orderid = fields.Integer('Order ID') # id
    requester_type = fields.Char() # requesterType
    requesterId = fields.Integer() # requesterId
    order_type = fields.Char() # orderType
    order_number = fields.Char() # orderNumber
    order_reference = fields.Char() # orderReference
    total = fields.Float() # total
    total_all = fields.Float() # totalAll
    status = fields.Char() # status
    request_delivery_date = fields.Datetime() # requestDeliveryDate
    notes = fields.Char() # notes
    receiver = None # receiver
    recipient_id = fields.Many2one('res.partner', 'Partner') # RecipientId
    internal_reference = fields.Char() # internalReference
    shippingId = None # ShippingId
    store_idd = None # storeId
    createdAt = fields.Datetime(readonly=True) # createdAt
    updatedAt = fields.Datetime(readonly=True) # updatedAt
    order_line_ids = fields.One2many('tada.order.line', 'order_id', 'Tada Order Items') # OrderItems
    fee_line_ids = fields.One2many('tada.fee', 'order_id', 'Tada Order Fees') # Fees
    payment_line_ids = fields.One2many('tada.payment', 'order_id', 'Tada Order Payments')
    
    def act_create_sale_order(self):
        team_id = self.env.ref('tada.salesteam_tada_sales')
        currency_id = None
        date_order = self.order_date
        name = None
        partner_id = None
        partner_invoice_id = None
        partner_shipping_id = None
        picking_policy = None
        pricelist_id = None
        warehouse_id = None
        vals = {'currency_id': currency_id,
                'date_order': date_order,
                'origin': name,
                'partner_id': partner_id.id,
                'partner_invoice_id': partner_invoice_id.id,
                'partner_shipping_id': partner_shipping_id.id,
                'picking_policy': picking_policy,
                'pricelist_id': pricelist_id.id,
                'warehouse_id': warehouse_id.id,
                'team_id': team_id.id}
        return
    
    @api.model
    def _get_on_tada(self, access_token=False):
        if not access_token:
            if self.tada_id:
                tada_id = self.tada_id
            else:
                return
        else:
            tada_id = self.mapped('tada_id').search([('access_token', '=', access_token)])
        Order = self.env['tada.order']
        Partner = self.env['res.partner']
        Variant = self.env['tada.product.variant']
        base_api_url = self.env['ir.config_parameter'].sudo().get_param('tada.base_api_url')
        authorization = 'Bearer {}'.format(access_token)
        headers = {'Content-Type': 'application/json', 'Authorization': authorization}
        latest_order_id = self.search([('tada_id', '=', tada_id.id)], order='createdAt desc', limit=1)
        body = {'page': 0}
        if latest_order_id.id:
            today = fields.Date.today()
            body.update({'periodStart': latest_order_id.createdAt, 'periodEnd': today})
        self._cr.execute('select id, orderid from %s where tada_id=%d' %(Order._table, tada_id.id))
        orders = {orderid: id for id, orderid in self._cr.fetchall()}
        self._cr.execute('select id, variantid from %s where tada_id=%d' %(Variant._table, tada_id.id))
        variants = {variantid: id for id, variantid in self._cr.fetchall()}
#         self._cr.execute('select id, tadaid from %s where tada_id=%d' %(Partner._table, tada_id.id))
#         customer = {variantid: id for id, tadaid in self._cr.fetchall()}
        count_item = 0
        has_next_page = True
        while has_next_page:
            body['page'] += 1
            bodyJson = json.dumps(body)
            auth_response = requests.post(base_api_url + OrderUrl, headers=headers, data=bodyJson, timeout=10.0)
            resp_json = auth_response.json()
            
            for order in resp_json['data']:
                count_item += 1
                orderid = order['id']
                requester_type = order['requesterType']
                requesterId = order['requesterId']
                order_type = order['orderType']
                order_number = order['orderNumber']
                order_reference = order['orderReference']
                total = order['total']
                total_all = order['totalAll']
                status = order['status']
                request_delivery_date = order['requestDeliveryDate']
                notes = order['notes']
#                 receiver = order['receiver']
#                 recipient_id = customers.get(order['RecipientId'], False)
                internal_reference = order['internalReference']
#                 shipping`Id = order['ShippingId']
#                 store_id = order['storeId']
                createdAt = order['createdAt']
                updatedAt = order['updatedAt']
                order_vals = {'tada_id': tada_id.id,
                            'orderid': orderid,
                            'requester_type': requester_type,
                            'requesterId': requesterId,
                            'order_type': order_type,
                            'order_number': order_number,
                            'order_reference': order_reference,
                            'total': total,
                            'total_all': total_all,
                            'status': status,
                            'request_delivery_date': request_delivery_date,
                            'notes': notes,
#                             'receiver': receiver,
#                             'recipient_id': recipient_id,
                            'internal_reference': internal_reference,
#                             'shippingId': shippingId,
#                             'store_id': store_id,
                            'createdAt': createdAt,
                            'updatedAt': updatedAt,}
                order_id = orders.get(orderid, False)
                if order_id:
                    Order.browse(order_id).write(order_vals)
                else:
                    Order.create(order_vals)
            self._cr.commit()
            if count_item == resp_json['totalItems']:
                has_next_page = False
        return
            
        

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
    
