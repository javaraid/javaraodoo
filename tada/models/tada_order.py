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
    payment_line_ids = fields.One2many('tada.payment', 'order_id', 'Tada Order Payments') # OrderPayments
    
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
    def _convert_resp_to_vals(self, tada_id, resp_dict):
        order = resp_dict
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
        return order_vals
    
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
        OrderLine = self.env['tada.order.line']
        Partner = self.env['res.partner']
        Variant = self.env['tada.product.variant']
        Payment = self.env['tada.payment']
        Fee = self.env['tada.fee']
        base_api_url = self.env['ir.config_parameter'].sudo().get_param('tada.base_api_url')
        authorization = 'Bearer {}'.format(access_token)
        headers = {'Content-Type': 'application/json', 'Authorization': authorization}
        latest_order_id = self.search([('tada_id', '=', tada_id.id)], order='createdAt desc', limit=1)
        body = {'page': 0}
        if latest_order_id.id:
            today = fields.Date.today()
            body.update({'periodStart': latest_order_id.createdAt.split(' ')[0], 'periodEnd': today})
        self._cr.execute('select id, orderid from %s where tada_id=%d' %(Order._table, tada_id.id))
        orders = {orderid: id for id, orderid in self._cr.fetchall()}
        self._cr.execute('select id, variantid from %s where tada_id=%d' %(Variant._table, tada_id.id))
        variants = {variantid: id for id, variantid in self._cr.fetchall()}
        count_item = 0
        has_next_page = True
        self._cr.execute('select id, tadaid, phone from {table} where customer=True;'.format(table=Partner._table))
        partner_fetched = self._cr.fetchall()
        customers_tada = {fetch[1]: fetch[0] for fetch in partner_fetched}
        customers_phone = {fetch[2]: fetch[1] for fetch in partner_fetched}
        while has_next_page:
            body['page'] += 1
            bodyJson = json.dumps(body)
            auth_response = requests.post(base_api_url + OrderUrl, headers=headers, data=bodyJson, timeout=10.0)
            resp_json = auth_response.json()
            if resp_json['totalItemPerPage'] == 0:
                break
            for order in resp_json['data']:
                count_item += 1
                orderid = order['id']
                partner_id = Partner._upsert_customer_tada(order['Recipient'], customers_tada, customers_phone)
                order_vals = self._convert_resp_to_vals(tada_id, order)
                order_vals['recipient_id'] = partner_id
                order_id = Order.browse(orders.get(orderid, False))
                if order_id:
                    order_id.write(order_vals)
                else:
                    order_id = Order.create(order_vals)
                # Appending Lines
                self._cr.execute('select id, orderlineid from %s where order_id=%d' %(OrderLine._table, order_id.id))
                order_lines = {orderlineid: id for id, orderlineid in self._cr.fetchall()}
                order_line = []
                for line in order['OrderItems']:
                    order_line_vals = OrderLine._convert_resp_to_vals(order_id.id, line, order_lines, variants)
                    order_line_id = order_lines.get(line['id'])
                    if order_line_id:
                        order_line.append((1, order_line_id, order_line_vals))
                    else:
                        order_line.append((0, 0, order_line_vals))
                self._cr.execute('select id, paymentid from %s where order_id=%d' %(Payment._table, order_id.id))
                payments = {paymentid: id for id, paymentid in self._cr.fetchall()}
                payment_line = []
                for payment in order['OrderPayments']:
                    payment_vals = Payment._convert_resp_to_vals(order_id.id, payment)
                    payment_id = payments.get(line['id'])
                    if payment_id:
                        payment_line.append((1, payment_id, payment_vals))
                    else:
                        payment_line.append((0, 0, payment_vals))
                self._cr.execute('select id, feeid from %s where order_id=%d' %(Fee._table, order_id.id))
                fees = {feeid: id for id, feeid in self._cr.fetchall()}
                fee_line = []
                for fee in order['Fees']:
                    fee_vals = Fee._convert_resp_to_vals(order_id.id, fee)
                    fee_id = fees.get(fee['id'], False)
                    if fee_id:
                        fee_line.append((1, fee_id, fee_vals))
                    else:
                        fee_line.append((0, 0, fee_vals))
                order_id.write({'order_line_ids': order_line, 'payment_line_ids': payment_line, 'fee_line_ids': fee_line})
                
            if count_item == resp_json['totalItems']:
                has_next_page = False
        return
    

class TadaOrderLine(models.Model):
    _name = 'tada.order.line'
    _description = 'Order Line Tada'
    
    orderlineid = fields.Integer() # id
    order_id = fields.Many2one('tada.order', 'Tada Order', index=True, ondelete='cascade', required=True) # OrderId
    variant_id = fields.Many2one('tada.product.variant', 'Variant') # variantId
    price = fields.Integer() # price
    quantity = fields.Integer() # quantity
    notes = fields.Char() # notes
    status = fields.Char() # status
    createdAt = fields.Datetime() # createdAt
    updatedAt = fields.Datetime() # updatedAt
    
    @api.model
    def _convert_resp_to_vals(self, order_id, resp_dict, order_lines=False, variants=False):
        Variant = self.env['tada.product.variant']
        if not variants:
            self._cr.execute('select id, variantid from %s where tada_id=%d' %(Variant._table, tada_id.id))
            variants = {variantid: id for id, variantid in self._cr.fetchall()}
        if not order_lines:
            self._cr.execute('select id, orderlineid from %s where order_id=%d' %(self._table, order_id))
            order_lines = {orderlineid: id for id, orderlineid in self._cr.fetchall()}
        orderlineid = resp_dict['id']
        variant_id = variants.get(resp_dict['variantId'], False)
        price = resp_dict['price']
        quantity = resp_dict['quantity']
        notes = resp_dict['notes']
        status = resp_dict['status']
        createdAt = resp_dict['createdAt']
        updatedAt = resp_dict['updatedAt']
        order_line_vals = {'orderlineid': orderlineid,
                           'order_id': order_id,
                           'variant_id': variant_id,
                           'price': price,
                           'quantity': quantity,
                           'notes': notes,
                           'status': status,
                           'createdAt': createdAt,
                           'updatedAt': updatedAt,}
        return order_line_vals
    
    
class TadaFee(models.Model):
    _name = 'tada.fee'
    _description = 'Fee Tada'
    
    feeid = fields.Integer() # id
    order_id = fields.Many2one('tada.order', 'Order', ondelete='cascade', index=True, required=True) # OrderId
    name = fields.Char() # name
    absorber = fields.Char() # absorber
    value = fields.Integer() # value
    createdAt = fields.Datetime(readonly=True) # createdAt
    updatedAt = fields.Datetime(readonly=True) # updatedAt
    
    @api.model
    def _convert_resp_to_vals(self, order_id, resp_dict):
        feeid = resp_dict['id']
        name = resp_dict['name']
        absorber = resp_dict['absorber']
        value = resp_dict['value']
        createdAt = resp_dict['createdAt']
        updatedAt = resp_dict['updatedAt']
        vals = {'feeid': feeid,
                'order_id': order_id,
                'name': name,
                'absorber': absorber,
                'value': value,
                'createdAt': createdAt,
                'updatedAt': updatedAt,}
        return vals
    
    
class TadaPayment(models.Model):
    _name = 'tada.payment'
    _description = 'Fee Tada'
    
    paymentid = fields.Integer() # id
    order_id = fields.Many2one('tada.order', 'Tada Order', index=True, ondelete='cascade') # OrderId
    payment_type = fields.Char() # paymentType
    channel = fields.Char() # channel
    card_number = fields.Char() # cardNumber
    amount = fields.Integer() # amount
    transactionId = fields.Char() # transactionId
    reward_type = fields.Char() # rewardType
    unit_type = fields.Char() # unitType
    conversion_rate = fields.Integer() # conversionRate
    currency_code = fields.Char() # currencyCode
    createdAt = fields.Datetime(readonly=True) # createdAt
    updatedAt = fields.Datetime(readonly=True) # updatedAt    
    
    @api.model
    def _convert_resp_to_vals(self, order_id, resp_dict):
        paymentid = resp_dict['id']
        payment_type = resp_dict['paymentType']
        channel = resp_dict['channel']
        card_number = resp_dict['cardNumber']
        amount = resp_dict['amount']
        transactionId = resp_dict['transactionId']
        reward_type = resp_dict['rewardType']
        unit_type = resp_dict['unitType']
        conversion_rate = resp_dict['conversionRate']
        currency_code = resp_dict['currencyCode']
        createdAt = resp_dict['createdAt']
        updatedAt = resp_dict['updatedAt']
        vals = {'paymentid': paymentid,
                'order_id': order_id,
                'payment_type': payment_type,
                'channel': channel,
                'card_number': card_number,
                'amount': amount,
                'transactionId': transactionId,
                'reward_type': reward_type,
                'unit_type': unit_type,
                'conversion_rate': conversion_rate,
                'currency_code': currency_code,
                'createdAt': createdAt,
                'updatedAt': updatedAt}
        return vals
    
    