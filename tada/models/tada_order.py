from datetime import date, timedelta
import requests
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

OrderUrl = '/v1/integration_merchants/manage/orders'
OrderDetailUrl = '/v1/integration_merchants/manage/orders/detail/{orderNumberOrId}'
OrderConfirmUrl = '/v1/integration_merchants/manage/orders/confirm'
OrderProcessUrl = '/v1/integration_merchants/manage/orders/process'
Headers = {'Content-Type': 'application/json', 'Authorization': None}


class TadaOrder(models.Model):
    _name = 'tada.order'
    _description = 'Order in Tada'
    _rec_name = 'order_number'
    _order = 'createdAt desc'
    
    tada_id = fields.Many2one('tada.tada', 'Tada Account', ondelete='cascade', required=True, index=True)
    orderid = fields.Integer('Order ID', readonly=True) # id
    requester_type = fields.Char(readonly=True) # requesterType
    requesterId = fields.Integer(readonly=True) # requesterId
    order_type = fields.Char(readonly=True) # orderType
    order_number = fields.Char(readonly=True) # orderNumber
    order_reference = fields.Char(readonly=True) # orderReference
    total = fields.Float(readonly=True) # total
    total_all = fields.Float(readonly=True) # totalAll
    status = fields.Char(readonly=True) # status
    request_delivery_date = fields.Datetime(readonly=True) # requestDeliveryDate
    notes = fields.Char(readonly=True) # notes
    receiver = None # receiver
    recipient_id = fields.Many2one('res.partner', 'Partner', readonly=True) # RecipientId
    recipientId = fields.Integer(readonly=True) # RecipientId
    recipientName = fields.Char(readonly=True) # Recipient.firstName
    internal_reference = fields.Char(readonly=True) # internalReference
    shippingId = None # ShippingId
    store_id = None # storeId
    createdAt = fields.Datetime(readonly=True) # createdAt
    updatedAt = fields.Datetime(readonly=True) # updatedAt
    order_line_ids = fields.One2many('tada.order.line', 'order_id', 'Tada Order Items', readonly=True) # OrderItems
    fee_line_ids = fields.One2many('tada.fee', 'order_id', 'Tada Order Fees', readonly=True) # Fees
    payment_line_ids = fields.One2many('tada.payment', 'order_id', 'Tada Order Payments', readonly=True) # OrderPayments
    sale_order_id = fields.Many2one('sale.order', 'Order', readonly=True)
    
    def act_create_sale_order(self):
        if self.status != 'payment success':
            raise ValidationError(_('Status of order %s is not payment success' %self.order_number))
        team_id = self.env.ref('tada.salesteam_tada_sales')
        currency_id = None
        date_order = self.createdAt
        name = self.order_number
        partner_id = self.recipient_id
#         partner_invoice_id = None
#         partner_shipping_id = None
        picking_policy = 'one'
        pricelist_id = partner_id.property_product_pricelist or self.env['product.pricelist'].search([], limit=1)
        warehouse_id = self.tada_id.warehouse_id
        vals = {'currency_id': currency_id,
                'date_order': date_order,
                'origin': name,
                'partner_id': partner_id.id,
#                 'partner_invoice_id': partner_invoice_id.id,
#                 'partner_shipping_id': partner_shipping_id.id,
                'picking_policy': picking_policy,
                'pricelist_id': pricelist_id.id,
                'warehouse_id': warehouse_id.id,
                'team_id': team_id.id,
                'is_from_tada': True}
        order_line_vals = self.order_line_ids._generate_sale_order_line()
        vals['order_line'] = [(0,0, vals) for vals in order_line_vals]
        sale_order_id = self.env['sale.order'].create(vals)
        self.sale_order_id= sale_order_id.id
        return
    
    def _action_confirm(self):
        sale_order_id = self.sale_order_id
        sale_order_id._action_confirm()
        sale_order_id.action_done()
        sale_payment_id = self.env['sale.advance.payment.inv'].with_context(active_ids=sale_order_id.ids, active_model='sale.order').create({'advance_payment_method': 'all'})
        sale_payment_id.create_invoices()
        sale_invoice_id = sale_order_id.invoice_ids
        sale_invoice_id.action_invoice_open()
        # karena katanya langsung ditransfer jadinya langsung di-register payment
        pay_journal = self.env['account.journal'].search([('is_tada_available', '=', True), ('company_id', '=', self.tada_id.warehouse_id.company_id.id)], limit=1)
        payment_vals = sale_invoice_id._prepare_payment_vals(pay_journal, pay_amount=self.total_all, date=self.updatedAt, writeoff_acc=None, communication=None)
        account_payment_id = self.env['account.payment'].create(payment_vals)
        account_payment_id.action_validate_invoice_payment()
        return
        
    def action_confirm(self):
        for rec in self:
            rec._action_confirm()
        base_api_url = self.env['ir.config_parameter'].sudo().get_param('tada.base_api_url')
        authorization = 'Bearer {}'.format(self.tada_id.access_token)
        headers = Headers.copy()
        headers['Authorization'] = authorization
        body = {'orderNumbers': self.mapped('order_number')}
        response = requests.post(base_api_url + OrderConfirmUrl, headers=headers, json=body, timeout=10.0)
        if response.status_code != 201:
            raise ValidationError(_('Error'))
        return
    
    def action_process(self):
        base_api_url = self.env['ir.config_parameter'].sudo().get_param('tada.base_api_url')
        authorization = 'Bearer {}'.format(self.tada_id.access_token)
        headers = Headers.copy()
        headers['Authorization'] = authorization
        body = {'orderNumbers': self.order_number}
        response = requests.post(base_api_url + OrderProcessUrl, headers=headers, json=body, timeout=10.0)
        if response.status_code != 201:
            raise ValidationError(_('Error'))
        return
    
    @api.model
    def _convert_resp_tada_to_vals(self, tada_id, resp_dict):
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
        recipientId = order['RecipientId']
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
        headers = Headers.copy()
        headers['Authorization'] = authorization
        latest_order_id = self.search([('tada_id', '=', tada_id.id)], order='createdAt desc', limit=1)
        body = {'page': 0}
        if latest_order_id.id:
            periodStart = latest_order_id.createdAt.split(' ')[0]
            periodEnd = str(date.today() + timedelta(days=1))
            body.update({'periodStart': periodStart, 'periodEnd': periodEnd})
        self._cr.execute('select id, orderid from %s where tada_id=%d' %(Order._table, tada_id.id))
        orders = {orderid: id for id, orderid in self._cr.fetchall()}
        self._cr.execute('select id, variantid from %s where tada_id=%d' %(Variant._table, tada_id.id))
        variants = {variantid: id for id, variantid in self._cr.fetchall()}
        count_item = 0
        has_next_page = True
        self._cr.execute('select id, tadaid, phone from {table} where customer=True;'.format(table=Partner._table))
        partner_fetched = self._cr.fetchall()
        customers_tada = {fetch[1]: fetch[0] for fetch in partner_fetched}
        customers_phone = {fetch[2]: fetch[0] for fetch in partner_fetched}
        while has_next_page:
            body['page'] += 1
            response = requests.post(base_api_url + OrderUrl, headers=headers, json=body, timeout=10.0)
            resp_json = response.json()
            if resp_json['totalItemPerPage'] == 0:
                break
            for order in resp_json['data']:
                count_item += 1
                orderid = order['id']
                Recipient = order['Recipient']
                partner_id = Partner._upsert_customer_tada(Recipient, customers_tada, customers_phone)
                order_vals = self._convert_resp_tada_to_vals(tada_id, order)
                order_vals['recipient_id'] = partner_id
                order_vals['recipientName'] = Recipient['firstName']
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
                    order_line_vals = OrderLine._convert_resp_tada_to_vals(order_id.id, line, order_lines, variants)
                    order_line_id = order_lines.get(line['id'])
                    if order_line_id:
                        order_line.append((1, order_line_id, order_line_vals))
                    else:
                        order_line.append((0, 0, order_line_vals))
                self._cr.execute('select id, paymentid from %s where order_id=%d' %(Payment._table, order_id.id))
                payments = {paymentid: id for id, paymentid in self._cr.fetchall()}
                payment_line = []
                for payment in order['OrderPayments']:
                    payment_vals = Payment._convert_resp_tada_to_vals(order_id.id, payment)
                    payment_id = payments.get(payment['id'])
                    if payment_id:
                        payment_line.append((1, payment_id, payment_vals))
                    else:
                        payment_line.append((0, 0, payment_vals))
                self._cr.execute('select id, feeid from %s where order_id=%d' %(Fee._table, order_id.id))
                fees = {feeid: id for id, feeid in self._cr.fetchall()}
                fee_line = []
                for fee in order['Fees']:
                    fee_vals = Fee._convert_resp_tada_to_vals(order_id.id, fee)
                    fee_id = fees.get(fee['id'], False)
                    if fee_id:
                        fee_line.append((1, fee_id, fee_vals))
                    else:
                        fee_line.append((0, 0, fee_vals))
                order_id.write({'order_line_ids': order_line, 'payment_line_ids': payment_line, 'fee_line_ids': fee_line})
                
            if count_item == resp_json['totalItems']:
                has_next_page = False
        return
    
    @api.model
    def _confirm_paid_order(self):
        paid_orders = self.search([('status', '=', 'payment success')])
        for paid_order in paid_orders:
            paid_order.act_create_sale_order()
        return
    
    @api.model
    def create(self, vals):
        order_id = self.sale_order_id.search([('origin', '=', vals['order_number'])], limit=1)
        vals.update({'sale_order_id': order_id.id})
        res = super(TadaOrder, self).create(vals)
        return res


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
    sku = fields.Char('SKU', related='variant_id.sku', readonly=True)
    
    @api.model
    def _convert_resp_tada_to_vals(self, order_id, resp_dict, order_lines=False, variants=False):
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
    
    
    def _generate_sale_order_line(self):
        vals_list = []
        bundling_product_ids = self.mapped('variant_id').mapped('bundling_quantity_ids')
        for rec in self:
            product_ids = rec.variant_id.system_product_ids
            if len(product_ids) == 0:
                raise ValidationError(_('Please create the product on system for SKU %s (%s)' %(rec.variant_id.sku, rec.variant_id.name)))
            sku_lst = rec.variant_id.sku.split(';')
            system_sku_lst = [product_id.default_code for product_id in product_ids] 
            for sku in sku_lst:
                if sku not in system_sku_lst:
                    raise ValidationError(_('Please create the product on system for SKU %s' %sku))
            for product_id in product_ids:
                quantity = rec.quantity
                bundling_id = bundling_product_ids.filtered(lambda product: product.id == product_id.id)
                if bundling_id.id:
                    quantity = bundling_id.quantity
                vals = {'product_id': product_id.id,
                        'name': product_id.name,
                        'product_uom_qty': quantity,
                        'price_unit': rec.price,
#                         'tax_id': ,
                        }
                vals_list.append(vals)
        return vals_list
    
    
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
    def _convert_resp_tada_to_vals(self, order_id, resp_dict):
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
    def _convert_resp_tada_to_vals(self, order_id, resp_dict):
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
    
    