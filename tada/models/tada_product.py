import requests
from odoo import models, fields, api

ProductUrl = '/v1/integration_merchants/manage/inventories/items'
ProductDetailUrl = '/v1/integration_merchants/manage/inventories/items/{itemid}'
VariantUrl = '/v1/integration_merchants/manage/inventories/items/{itemid}/variants'
VariantDetailUrl = '/v1/integration_merchants/manage/inventories/items/{itemid}/variants/{variantId}'
CategoryUrl = '/v1/integration_merchants/manage/inventories/categories'
CatalogUrl = '/v1/integration_merchants/manage/inventories/catalogs/{catalogId}/categories'

class TadaCategory(models.Model):
    _name = 'tada.category'
    _description = 'Tada Categories'
    
    tada_id = fields.Many2one('tada.tada', 'Tada Account', ondelete='cascade')
    categid = fields.Integer(readonly=True) # id
    parent_id = fields.Many2one(_name, 'Parent') # parentId
    mId = fields.Char(readonly=True) # mId
    name = fields.Char() # name
    label = fields.Char() # label
    active = fields.Boolean(default=True) # active
    groupRefId = None # groupRefId
    createdAt = fields.Datetime(readonly=True) # createdAt
    updatedAt = fields.Datetime(readonly=True) # updatedAt
    child_ids = fields.One2many(_name, 'parent_id', 'Childs') # childs
    product_ids = fields.One2many('tada.product', 'category_id', 'Products')
    
    def act_sync(self):
        self._get_on_tada()
    
    @api.model
    def _get_on_tada(self, access_token=False):
        if not access_token:
            if self.tada_id:
                tada_id = self.tada_id
            else:
                return
        else:
            tada_id = self.mapped('tada_id').search([('access_token', '=', access_token)])
        base_api_url = self.env['ir.config_parameter'].sudo().get_param('tada.base_api_url')
        authorization = 'Bearer {}'.format(access_token)
        headers = {'Content-Type': 'application/json', 'Authorization': authorization}
        auth_response = requests.get(base_api_url + CategoryUrl, headers=headers, timeout=10.0)
        resp_json = auth_response.json()
        self._cr.execute('select id, categid from %s where tada_id=%d' %self._table, tada_id.id)
        categories = {categid: id for id, categid in self._cr.fetchall()}
        parent_not_found = {}
        for resp in resp_json['data']:
            mId = resp['mId']
            active = resp['active']
            categid = resp['id']
            createdAt = resp['createdAt']
            updatedAt = resp['updatedAt']
            # groupRefId = resp['groupRefId']
            name = resp['name']
            label = resp['label']
            parentId = resp['parentId']
            parent_id = categories.get(parentId, False)
            vals = {'tada_id': tada_id.id,
                    'categid': categid,
                    'parent_id': parent_id,
                    'mId': mId,
                    'name': name,
                    'label': label,
                    'active': active,
                    'createdAt': createdAt,
                    'updatedAt': updatedAt,
                    }
            categ_id = self.browse(categories.get(categid, False))
            if not categ_id.id:
                categ_id = self.create(vals)
            elif categ_id.updatedAt <  updatedAt.replace('T', ' ').replace('Z', ''):
                categ_id.write(vals)
            if parentId  and not parent_id:
                if not parent_not_found.get(parentId, False):
                    parent_not_found.update({parentId: [categ_id.id]})
                else:
                    parent_not_found[parentId].append(categ_id.id)
            categories.update({categid: categ_id.id})
        self._cr.commit()
        for parent_id, child_ids in parent_not_found.items():
            parent_id = categories.get(categ_id, False)
            if parent_id:
                self._cr.execute('update %s set parent_id=parent_id where id in %s', (self._table, tuple(child_ids)))
                self._cr.commit()
    
    @api.model
    def create(self, vals):
        res = super(TadaCategory, self).create(vals)
        return res
    
    
class TadaProduct(models.Model):
    _name = 'tada.product'
    _description = 'Tada Products'
    
    tada_id = fields.Many2one('tada.tada', 'Tada Account', ondelete='cascade')
    productid = fields.Integer(index=True, readonly=True) # id
    category_id = fields.Many2one('tada.category', 'Category') # CategoryId
    VendorId = None # VendorId
    is_digital = fields.Boolean() # isDigital
    item_type = fields.Char('Type') # itemType
    swap_redeem = fields.Char() # swapRedeem
    name = fields.Char(required=True) # name
    description = fields.Html(compute='_compute_description', inverse='_inverse_description', store=True) # description
    image = fields.Char(compute='_compute_image', inverse='_inverse_image', store=True) # image
    prefix = None # prefix
    delivery_type = fields.Char() # deliveryType
    is_limited = fields.Boolean() # isLimited
    limit_qty = fields.Integer() # limitQty
    gcfsItemId = None # gcfsItemId
    active = fields.Boolean(default=True) # active
    enable_store_availability = fields.Boolean() # enableStoreAvailability
    store_ids = fields.Many2many('tada.store', string='Available on Store')
    createdAt = fields.Datetime(readonly=True) # createdAt
    updatedAt = fields.Datetime(readonly=True) # updatedAt
    price = fields.Integer(default=0, required=False, compute='_compute_price', inverse='_inverse_price', store=True)
    image_view = fields.Char(related='image')
    variant_ids = fields.One2many('tada.product.variant', 'product_id', 'Product Variants')
    has_variant = fields.Boolean(compute='_compute_has_variant', store=True)
    system_product_ids = fields.Many2many('product.product', string='Products on System', compute='_compute_system_product')
    
    def _compute_system_product(self):
        for rec in self:
            rec
        return
    
    @api.depends('variant_ids.price')
    def _compute_price(self):
        for rec in self:
            if rec.has_variant:
                continue
            rec.price = rec.variant_ids.price
        return
    
    def _inverse_price(self):
        if self.has_variant:
            return
        self.variant_ids.price = self.price
        return
    
    @api.depends('variant_ids.image')
    def _compute_image(self):
        for rec in self:
            if rec.has_variant:
                continue
            rec.price = rec.variant_ids.price
        
    def _inverse_image(self):
        if self.has_variant:
            return
        self.variant_ids.price = self.price
        return
    
    @api.depends('variant_ids.description')
    def _compute_description(self):
        for rec in self:
            if rec.has_variant:
                continue
            rec.description = rec.variant_ids.description
        
    def _inverse_description(self):
        if self.has_variant:
            return
        self.variant_ids.description = self.description
        return
    
    @api.depends('variant_ids')
    def _compute_has_variant(self):
        for rec in self:
            rec.has_variant = len(rec.variant_ids) > 1
        return
        
    def act_get_variant(self):
        base_api_url = self.env['ir.config_parameter'].sudo().get_param('tada.base_api_url')
        authorization = 'Bearer {}'.format(access_token)
        headers = {'Content-Type': 'application/json', 'Authorization': authorization}
        auth_response = requests.get(base_api_url + VariantUrl.format(itemid=productid), headers=headers, timeout=10.0)
        resp_json = auth_response.json()
        return
    
    def _update_to_tada(self):
        return
    
    def act_sync(self):
        self = self.with_context(sync=True)
        Stock = self.env['tada.stock']
        Category = self.env['tada.category']
        Variant = self.env['tada.product.variant']
        tada_id = self.tada_id
        base_api_url = self.env['ir.config_parameter'].sudo().get_param('tada.base_api_url')
        access_token = tada_id.access_token
        authorization = 'Bearer {}'.format(access_token)
        headers = {'Content-Type': 'application/json', 'Authorization': authorization}
        auth_response = requests.get(base_api_url + ProductDetailUrl.format(itemid=self.productid), headers=headers, timeout=10.0)
        resp_json = auth_response.json()
        self._cr.execute('select id, categid from %s where tada_id=%d' %Category._table, tada_id.id)
        categories = {categid: id for id, categid in self._cr.fetchall()}
        self._cr.execute('select id, variantid from %s where product_id=%d' %(Variant._table, self.id))
        variants = {variant: id for id, variantid in self._cr.fetchall()}
        self._cr.execute('select id, stockid from %s' %(Stock._table))
        stocks = {stockid: id for id, stockid in self._cr.fetchall()}
        productid = resp_json['id']
        category_id = categories.get(resp_json['CategoryId'], False)
        is_digital = resp_json['isDigital']
        item_type = resp_json['itemType']
        swap_redeem = resp_json['swapRedeem']
        name = resp_json['name']
        description = resp_json['description']
        image = resp_json['image']
        delivery_type = resp_json['deliveryType']
        is_limited = resp_json['isLimited']
        limit_qty = resp_json['limitQty']
        active = resp_json['active']
        createdAt = resp_json['createdAt']
        updatedAt = resp_json['updatedAt']
        vals = {'productid': productid,
                'category_id': category_id,
                'is_digital': is_digital,
                'item_type': item_type,
                'swap_redeem': swap_redeem,
                'name': name,
                'description': description,
                'image': image,
                'delivery_type': delivery_type,
                'is_limited': is_limited,
                'limit_qty': limit_qty,
                'active': active,
                'tada_id': tada_id.id,
                'createdAt': createdAt,
                'updatedAt': updatedAt,}
        variant_line = []
        for variant in resp_json['Variants']:
            variantid = variant['id']
            name = variant['name']
            description = variant['description']
            image = variant['image']
            sku = variant['sku']
            value_type = variant['valueType']
            min_price = variant['minPrice']
            is_multi_price = variant['isMultiPrice']
            price = variant['price']
            source_type = variant['sourceType']
            active = variant['active']
            createdAt = variant['createdAt']
            updatedAt = variant['updatedAt']
            variant_vals = {'variantid': variantid,
                            'name': name,
                            'description': description,
                            'image': image,
                            'sku': sku,
                            'value_type': value_type,
                            'min_price': min_price,
                            'is_multi_price': is_multi_price,
                            'price': price,
                            'source_type': source_type,
                            'active': active,
                            'createdAt': createdAt,
                            'updatedAt': updatedAt,
                            }
            variant_id = variants.get(variantid, False)
            stock = variant['Stock']
            stockid = stock['id']
            stock_id = stocks.get(stockid, False)
            if not stock_id:
                stock_type = stock['stockType']
                name = stock['name']
                terms = stock['terms']
                price = stock['price']
                default_exp_type = stock['defaultExpType']
                default_exp = stock['defaultExp']
                default_exp_date = stock['defaultExpDate']
                is_limited = stock['isLimited']
                quantity = stock['quantity']
                image = stock['image']
                weight = stock['weight']
                length = stock['length']
                height = stock['height']
                width = stock['width']
                active = stock['active']
                createdAt = stock['createdAt']
                updatedAt = stock['updatedAt']
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
                stock_id = Stock.create(stock_vals).id
                stocks.update({stockid: stock_id})
            variant_vals['stock_id'] = stock_id
            if variant_id:
                variant_line.append((1, variant_id, variant_vals))
            else:
                variant_line.append((0, 0, variant_vals))
        self.write(vals)
    
    @api.model
    def _get_on_tada(self, access_token=False):
        if not access_token:
            if self.tada_id:
                tada_id = self.tada_id
            else:
                return
        else:
            tada_id = self.mapped('tada_id').search([('access_token', '=', access_token)])
        base_api_url = self.env['ir.config_parameter'].sudo().get_param('tada.base_api_url')
        authorization = 'Bearer {}'.format(access_token)
        headers = {'Content-Type': 'application/json', 'Authorization': authorization}
        has_next_page = True
        count_item = 0
        params = {'page': 0}
        while has_next_page:
            params['page'] += 1
            auth_response = requests.get(base_api_url + ProductUrl, params=params, headers=headers, timeout=10.0)
            resp_json = auth_response.json()
            self._cr.execute('select id, categid from %s where tada_id=%d' %(self.mapped('category_id')._table, tada_id.id))
            categories = {categid: id for id, categid in self._cr.fetchall()}
            self._cr.execute('select id, productid from %s where tada_id=%d' %(self._table, tada_id.id))
            products = {prodid: id for id, prodid in self._cr.fetchall()}
            for resp in resp_json['data']:
                count_item += 1
                productid = resp['id']
                category_id = categories.get(resp['CategoryId'], False)
                is_digital = resp['isDigital']
                item_type = resp['itemType']
                swap_redeem = resp['swapRedeem']
                name = resp['name']
                description = resp['description']
                image = resp['image']
                delivery_type = resp['deliveryType']
                is_limited = resp['isLimited']
                limit_qty = resp['limitQty']
                active = resp['active']
                createdAt = resp['createdAt']
                updatedAt = resp['updatedAt']
                vals = {'productid': productid,
                        'category_id': category_id,
                        'is_digital': is_digital,
                        'item_type': item_type,
                        'swap_redeem': swap_redeem,
                        'name': name,
                        'description': description,
                        'image': image,
                        'delivery_type': delivery_type,
                        'is_limited': is_limited,
                        'limit_qty': limit_qty,
                        'active': active,
                        'tada_id': tada_id.id,
                        'createdAt': createdAt,
                        'updatedAt': updatedAt,}
                product_id = self.browse(products.get(productid, False))
                if not product_id.id:
                    product_id = self.create(vals)
                elif not product_id.updatedAt or product_id.updatedAt <  updatedAt.replace('T', ' ').replace('Z', ''):
                    product_id.write(vals)
            if count_item == resp_json['count']:
                has_next_page = False
    
    @api.model
    def create(self, vals):
        res = super(TadaProduct, self).create(vals)
        return res
    
    def write(self, vals):
        res = super(TadaProduct, self).write(vals)
        if not self._context.get('sync'):
            self._update_to_tada()
        return res
    
    
class TadaProductVariant(models.Model):
    _name = 'tada.product.variant'
    _description = 'Tada Products Variant'
    
    product_id = fields.Many2one('tada.product', 'Product', required=True, index=True)
    tada_id = fields.Many2one('tada.tada', 'Tada', related='product_id.tada_id', store=True, index=True)
    variantid = fields.Integer(readonly=True) # id
    name = fields.Char(required=True) # name
    description = fields.Html() # description
    image = fields.Char() # image
    sku = fields.Char('SKU') # sku
    value_type = fields.Char() # valueType
    min_price = fields.Integer() # minPrice
    is_multi_price = fields.Boolean() # isMultiPrice
    price = fields.Integer(default=0, required=False) # price
    source_type = fields.Char() # sourceType
    active = fields.Boolean(default=True) # active
    createdAt = fields.Datetime(readonly=True) # createdAt
    updatedAt = fields.Datetime(readonly=True) # updatedAt
    stock_id = fields.Many2one('tada.stock', 'Stocks', required=False, index=True)
    image_view = fields.Char(related='image')
    system_product_ids = fields.Many2many('product.product', string='Products on System', compute='_compute_system_product', store=True)
    
    @api.depends('sku')
    def _compute_system_product(self):
        Product = self.env['product.product']
        for rec in self:
            sku_lst = rec.sku.split(';')
            if len(sku_lst) == 1:
                operator = '='
                sku = sku_lst[0]
            else:
                operator = 'in'
                sku = sku_lst
            
            system_product_ids = Product.search([('default_code', operator, sku)])
            rec.system_product_ids = [(6,0,system_product_ids.ids)]
        return
    
    @api.model
    def _update_product_variant(self, itemid, vals):
        product_id = self.search([('productid', '=', itemid)])
    
    def act_sync(self):
        self = self.with_context(sync=True)
        Stock = self.env['tada.stock']
        Category = self.env['tada.category']
        Product = self.env['tada.product']
        product_id = self.product_id
        tada_id = product_id.tada_id
        base_api_url = self.env['ir.config_parameter'].sudo().get_param('tada.base_api_url')
        access_token = tada_id.access_token
        authorization = 'Bearer {}'.format(access_token)
        headers = {'Content-Type': 'application/json', 'Authorization': authorization}
        auth_response = requests.get(base_api_url + VariantDetailUrl.format(itemid=product_id.productid, variantId=self.variantid), headers=headers, timeout=10.0)
        resp_json = auth_response.json()
        self._cr.execute('select id, variantid from %s where product_id=%d' %(self._table, product_id.id))
        variants = {variantid: id for id, variantid in self._cr.fetchall()}
        self._cr.execute('select id, stockid from %s' %(Stock._table))
        stocks = {stockid: id for id, stockid in self._cr.fetchall()}
        variant = resp_json
        variantid = variant['id']
        name = variant['name']
        description = variant['description']
        image = variant['image']
        sku = variant['sku']
        value_type = variant['valueType']
        min_price = variant['minPrice']
        is_multi_price = variant['isMultiPrice']
        price = variant['price']
        source_type = variant['sourceType']
        active = variant['active']
        createdAt = variant['createdAt']
        updatedAt = variant['updatedAt']
        variant_vals = {'variantid': variantid,
                        'name': name,
                        'description': description,
                        'image': image,
                        'sku': sku,
                        'value_type': value_type,
                        'min_price': min_price,
                        'is_multi_price': is_multi_price,
                        'price': price,
                        'source_type': source_type,
                        'active': active,
                        'createdAt': createdAt,
                        'updatedAt': updatedAt,
                        }
        variant_id = variants.get(variantid, False)
        stock = variant['Stock']
        stockid = stock['id']
        stock_id = stocks.get(stockid, False)
        if not stock_id:
            stock_type = stock['stockType']
            name = stock['name']
            terms = stock['terms']
            price = stock['price']
            default_exp_type = stock['defaultExpType']
            default_exp = stock['defaultExp']
            default_exp_date = stock['defaultExpDate']
            is_limited = stock['isLimited']
            quantity = stock['quantity']
            image = stock['image']
            weight = stock['weight']
            length = stock['length']
            height = stock['height']
            width = stock['width']
            active = stock['active']
            createdAt = stock['createdAt']
            updatedAt = stock['updatedAt']
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
            stock_id = Stock.create(stock_vals).id
            stocks.update({stockid: stock_id})
        variant_vals['stock_id'] = stock_id
        if variant_id:
            self.browse(variant_id).write(variant_vals)
        else:
            self.create(variant_vals)
        return
    
