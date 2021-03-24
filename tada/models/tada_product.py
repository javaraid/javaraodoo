import json
import requests
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

ProductUrl = '/v1/integration_merchants/manage/inventories/items'
ProductDetailUrl = '/v1/integration_merchants/manage/inventories/items/{itemid}'
VariantUrl = '/v1/integration_merchants/manage/inventories/items/{itemid}/variants'
VariantDetailUrl = '/v1/integration_merchants/manage/inventories/items/{itemid}/variants/{variantId}'
CategoryUrl = '/v1/integration_merchants/manage/inventories/categories'
CategoryDetailUrl = '/v1/integration_merchants/manage/inventories/categories/{categoryId}'
CatalogUrl = '/v1/integration_merchants/manage/inventories/catalogs/{catalogId}/categories'
ValidateSkuUrl = '/v1/integration_merchants/manage/inventories/items/{itemid}/variants/validate_sku?sku={sku}'
Headers = {'Content-Type': 'application/json', 'Authorization': None}

TadaCategoryFields = {'parent_id','name','label','active','createdAt','updatedAt',}
TadaCategoryFieldsName = {'parent_id': 'parentId',
                        'name': 'name',
                        'label': 'label',
                        'active': 'active',
                        'createdAt': 'createdAt',
                        'updatedAt': 'updatedAt',}
TadaProductFields = {'category_id', 'is_digital','item_type','swap_redeem','name','description','image','delivery_type','is_limited','limit_qty','active','enable_store_availability','createdAt','updatedAt'}
TadaProductFieldsName = {'category_id': 'CategoryId',
                        'is_digital': 'isDigital',
                        'item_type': 'itemType',
                        'swap_redeem': 'swapRedeem',
                        'name': 'name',
                        'description': 'description',
                        'image': 'image',
                        'delivery_type': 'deliveryType',
                        'is_limited': 'isLimited',
                        'limit_qty': 'limitQty',
                        'active': 'active',
                        'enable_store_availability': 'enableStoreAvailability',
                        'createdAt': 'createdAt',
                        'updatedAt': 'updatedAt'} 
TadaVariantFields = {'name','description','image','sku','value_type','min_price','is_multi_price','price','source_type','active','createdAt','updatedAt'}
TadaVariantFieldsName = {'variantid': 'id',
                        'name': 'name',
                        'description': 'description',
                        'image': 'image',
                        'sku': 'sku',
                        'value_type': 'valueType',
                        'min_price': 'minPrice',
                        'is_multi_price': 'isMultiPrice',
                        'price': 'price',
                        'source_type': 'sourceType',
                        'active': 'active',
                        'createdAt': 'createdAt',
                        'updatedAt': 'updatedAt'}


class TadaCategory(models.Model):
    _name = 'tada.category'
    _description = 'Tada Categories'
    
    tada_id = fields.Many2one('tada.tada', 'Tada Account', ondelete='cascade', required=True)
    categid = fields.Integer(readonly=True) # id
    parent_id = fields.Many2one(_name, 'Parent') # parentId
    mId = fields.Char(readonly=True) # mId
    name = fields.Char() # name
    label = fields.Char(default=lambda self: self.name) # label
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
                tada_id.check_token_validity()
                access_token = tada_id.access_token
            else:
                return
        else:
            tada_id = self.mapped('tada_id').search([('access_token', '=', access_token)])
        base_api_url = self.env['ir.config_parameter'].sudo().get_param('tada.base_api_url')
        authorization = 'Bearer {}'.format(access_token)
        headers = Headers.copy()
        headers['Authorization'] = authorization
        response = requests.get(base_api_url + CategoryUrl, headers=headers, timeout=50.0)
        resp_json = response.json()
        self._cr.execute('select id, categid from %s where tada_id=%d' %(self._table, tada_id.id))
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
        if not self._context.get('sync', False):
            res._create_to_tada(vals)
        return res
    
    def write(self, vals):
        res = super(TadaCategory, self).write(vals)
        if not self._context.get('sync', False):
            self._update_to_tada(vals)
        return res
    
    def _create_to_tada(self, vals):
        self.tada_id.check_token_validity()
        access_token = self.tada_id.access_token
        base_api_url = self.env['ir.config_parameter'].sudo().get_param('tada.base_api_url')
        authorization = 'Bearer {}'.format(access_token)
        headers = Headers.copy()
        headers['Authorization'] = authorization
        body = {"name": vals.get('name'),
                "allowedPayments": [
                    "EXTERNAL_PAYMENT"
                  ]
                }
        response = requests.post(base_api_url + CategoryUrl, headers=headers, json=body, timeout=50.0)
        resp_json = response.json()
        if response.status_code != 200 or len(resp_json.get('failed', [])) != 0:
            if 'message' in resp_json:
                message = resp_json['message']
            elif 'failed' in resp_json:
                message = resp_json['failed'][0]['message']
            else:
                message = 'Error'
            raise ValidationError(_(message))
        resp_vals = {'categid': resp_json['id'],
                    'parent_id': resp_json['parent_id'],
                    'mId': resp_json['mId'],
                    'name': resp_json['name'],
                    'label': resp_json['label'],
                    'active': resp_json['active'],
                    'createdAt': resp_json['createdAt'],
                    'updatedAt': resp_json['updatedAt']}
        return self.with_context(sync=True).write(resp_vals)
    
    def _update_to_tada(self, vals):
        updated_fields = set(vals.keys())
        difference_field = updated_fields.difference(TadaCategoryFields)
        for field in difference_field:
            vals.pop(field)
        if len(vals) == 0:
            return
        body = {TadaCategoryFieldsName[key]: value for key, value in vals.items()}
        if 'parent_id' in vals:
            body.update({'parentId': self.parent_id.categid or None})
        body.update(name=vals.get('name', self.name))
        bodyJson = json.dumps(body)
        base_api_url = self.env['ir.config_parameter'].sudo().get_param('tada.base_api_url')
        self.tada_id.check_token_validity()
        access_token = self.tada_id.access_token
        authorization = 'Bearer {}'.format(access_token)
        headers = Headers.copy()
        headers['Authorization'] = authorization
        response = requests.put(base_api_url + CategoryDetailUrl.format(categoryId=self.categid), headers=headers, data=bodyJson, timeout=50.0)
        resp_json = response.json()
        if response.status_code != 200 or len(resp_json.get('failed', [])) != 0:
            if 'message' in resp_json:
                message = resp_json['message']
            elif 'failed' in resp_json:
                message = resp_json['failed'][0]['message']
            else:
                message = 'Error'
            raise ValidationError(_(message))
        self.with_context(sync=True).write({'updatedAt': resp_json['updatedAt']})
        return
    
    
class TadaProduct(models.Model):
    _name = 'tada.product'
    _description = 'Tada Products'
    
    tada_id = fields.Many2one('tada.tada', 'Tada Account', ondelete='cascade', required=True)
    productid = fields.Integer(index=True, readonly=True) # id
    category_id = fields.Many2one('tada.category', 'Category') # CategoryId
    VendorId = None # VendorId
    is_digital = fields.Boolean() # isDigital
    item_type = fields.Char(default="item") # itemType
    swap_redeem = fields.Char() # swapRedeem
    name = fields.Char(required=True) # name
    description = fields.Html(compute='_compute_description', inverse='_inverse_description', store=True) # description
    image = fields.Char(compute='_compute_image', inverse='_inverse_image', store=True) # image
    prefix = None # prefix
    delivery_type = fields.Char() # deliveryType
    is_limited = fields.Boolean(default=True) # isLimited
    limit_qty = fields.Integer() # limitQty
    gcfsItemId = None # gcfsItemId
    variant_ids = fields.One2many('tada.product.variant', 'product_id', 'Product Variants', readonly=True) # Variants
    active = fields.Boolean(default=True) # active
    enable_store_availability = fields.Boolean() # enableStoreAvailability
    store_ids = fields.Many2many('tada.store', string='Available on Store') # stores
    createdAt = fields.Datetime(readonly=True) # createdAt
    updatedAt = fields.Datetime(readonly=True) # updatedAt
    price = fields.Integer(default=0, required=False, compute='_compute_price', inverse='_inverse_price', store=True)
    quantity = fields.Integer(compute='_compute_quantity', inverse='_inverse_quantity', store=True)
    sku = fields.Char(compute='_compute_sku', inverse='_inverse_sku', store=True)
    image_view = fields.Char(related='image')
    has_variant = fields.Boolean(compute='_compute_has_variant', store=True)
    count_variant = fields.Boolean(compute='_compute_has_variant', store=True)
    system_product_ids = fields.Many2many('product.product', string='Products on System', compute='_compute_system_product')
    bundling_quantity_ids = fields.One2many('tada.product.bundling.quantity', 'product_id', 'Bundling Quantity')
    
    @api.depends('variant_ids.quantity')
    def _compute_quantity(self):
        for rec in self:
            if len(rec.variant_ids) == 1:
                rec.quantity = rec.variant_ids.quantity
        return
    
    def _inverse_quantity(self):
        if not self.has_variant and self.count_variant != 0:
            self.variant_ids.quantity = self.quantity
        return
    
    @api.depends('variant_ids.sku')
    def _compute_sku(self):
        for rec in self:
            if len(rec.variant_ids) == 1:
                rec.sku = rec.variant_ids.sku
        return
    
    def _inverse_sku(self):
        if not self.has_variant and self.count_variant != 0:
            self.variant_ids.sku = self.sku
        return
    
    def _compute_system_product(self):
        for rec in self:
            rec.system_product_ids = rec.variant_ids.mapped('system_product_ids')
        return
    
    @api.depends('variant_ids.price')
    def _compute_price(self):
        for rec in self:
            if rec.has_variant:
                continue
            rec.price = rec.variant_ids.price
        return
    
    def _inverse_price(self):
        if not self.has_variant and self.count_variant != 0:
            self.variant_ids.price = self.price
        return
    
    @api.depends('variant_ids.image')
    def _compute_image(self):
        for rec in self:
            if rec.has_variant:
                continue
            rec.image = rec.variant_ids.image
        
    def _inverse_image(self):
        if not self.has_variant and self.count_variant != 0:
            self.variant_ids.image = self.image
        return
    
    @api.depends('variant_ids.description')
    def _compute_description(self):
        for rec in self:
            if rec.has_variant:
                continue
            rec.description = rec.variant_ids.description
        
    def _inverse_description(self):
        if not self.has_variant and self.count_variant != 0:
            self.variant_ids.description = self.description
        return
    
    @api.depends('variant_ids')
    def _compute_has_variant(self):
        for rec in self:
            len_variant = len(rec.variant_ids)
            rec.count_variant = len_variant
            rec.has_variant = len_variant > 1
        return
    
    @api.model
    def _convert_resp_tada_to_vals(self, tada_id, resp_dict, categories=False, variants=False, stocks=False):
        Category = self.env['tada.category']
        Variant = self.env['tada.product.variant']
        Stock = self.env['tada.stock']
        if not categories:
            self._cr.execute('select id, categid from %s where tada_id=%d' % (Category._table, tada_id.id))
            categories = {categid: id for id, categid in self._cr.fetchall()}
        if not stocks:
            self._cr.execute('select id, stockid from %s' %(Stock._table))
            stocks = {stockid: id for id, stockid in self._cr.fetchall()}
        if not variants:
            self._cr.execute('select id, variantid from %s where product_id=%d' %(Variant._table, self.id))
            variants = {variantid: id for id, variantid in self._cr.fetchall()}
        productid = resp_dict['id']
        category_id = categories.get(resp_dict['CategoryId'], False)
        is_digital = resp_dict['isDigital']
        item_type = resp_dict['itemType']
        swap_redeem = resp_dict['swapRedeem']
        name = resp_dict['name']
        description = resp_dict['description']
        image = resp_dict['image']
        delivery_type = resp_dict['deliveryType']
        is_limited = resp_dict['isLimited']
        limit_qty = resp_dict['limitQty']
        active = resp_dict['active']
        enable_store_availability = resp_dict['enableStoreAvailability']
        createdAt = resp_dict['createdAt']
        updatedAt = resp_dict['updatedAt']
        vals = {'tada_id': tada_id.id,
                'productid': productid,
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
                'enable_store_availability': enable_store_availability,
                'createdAt': createdAt,
                'updatedAt': updatedAt,}
        variant_line = []
        for variant in resp_dict['Variants']:
            variant_vals = Variant._convert_resp_tada_to_vals(variant, stocks)
            variantid = variant['id']
            variant_id = variants.get(variantid, False)
            if variant_id:
                variant_line.append((1, variant_id, variant_vals))
            else:
                variant_line.append((0, 0, variant_vals))
        vals['variant_ids'] = variant_line
        return vals
    
    def act_sync(self):
        self = self.with_context(sync=True)
        Category = self.env['tada.category']
        Variant = self.env['tada.product.variant']
        Stock = self.env['tada.stock']
        tada_id = self.tada_id
        base_api_url = self.env['ir.config_parameter'].sudo().get_param('tada.base_api_url')
        tada_id.check_token_validity()
        access_token = tada_id.access_token
        authorization = 'Bearer {}'.format(access_token)
        headers = Headers.copy()
        headers['Authorization'] = authorization
        response = requests.get(base_api_url + ProductDetailUrl.format(itemid=self.productid), headers=headers, timeout=50.0)
        resp_json = response.json()
        self._cr.execute('select id, categid from %s where tada_id=%d' % (Category._table, tada_id.id))
        categories = {categid: id for id, categid in self._cr.fetchall()}
        self._cr.execute('select id, variantid from %s where product_id=%d' %(Variant._table, self.id))
        variants = {variantid: id for id, variantid in self._cr.fetchall()}
        self._cr.execute('select id, stockid from %s' %(Stock._table))
        stocks = {stockid: id for id, stockid in self._cr.fetchall()}
        vals = self._convert_resp_tada_to_vals(tada_id, resp_json, categories, variants, stocks)
        self.write(vals)
        tada_id.name = resp_json['Merchant']['company']
    
    @api.model
    def _get_on_tada(self, access_token=False):
        if not access_token:
            if self.tada_id:
                tada_id = self.tada_id
                tada_id.check_token_validity()
                access_token = tada_id.access_token
            else:
                return
        else:
            tada_id = self.mapped('tada_id').search([('access_token', '=', access_token)])
        self = self.with_context(sync=True)
        Category = self.env['tada.category']
        Variant = self.env['tada.product.variant']
        Stock = self.env['tada.stock']
        base_api_url = self.env['ir.config_parameter'].sudo().get_param('tada.base_api_url')
        authorization = 'Bearer {}'.format(access_token)
        headers = Headers.copy()
        headers['Authorization'] = authorization
        self._cr.execute('select id, categid from %s where tada_id=%d' %(self.mapped('category_id')._table, tada_id.id))
        categories = {categid: id for id, categid in self._cr.fetchall()}
        self._cr.execute('select id, productid from %s where tada_id=%d' %(self._table, tada_id.id))
        products = {prodid: id for id, prodid in self._cr.fetchall()}
        self._cr.execute('select id, stockid from %s' %(Stock._table))
        stocks = {stockid: id for id, stockid in self._cr.fetchall()}
        sql = 'select id, variantid from %s' %(Variant._table)
        if self.id:
            sql += ' where product_id=%d' %self.id
        self._cr.execute(sql)
        variants = {variantid: id for id, variantid in self._cr.fetchall()}
        has_next_page = True
        count_item = 0
        params = {'page': 0}
        resp = None
        while has_next_page:
            params['page'] += 1
            response = requests.get(base_api_url + ProductUrl, params=params, headers=headers, timeout=50.0)
            resp_json = response.json()
            for resp in resp_json['data']:
                count_item += 1
                productid = resp['id']
                vals = self._convert_resp_tada_to_vals(tada_id, resp, categories, variants, stocks)
                product_id = self.browse(products.get(productid, False))
                updatedAt = resp['updatedAt']
                if not product_id.id:
                    product_id = self.create(vals)
                elif not product_id.updatedAt or product_id.updatedAt <  updatedAt.replace('T', ' ').replace('Z', ''):
                    product_id.write(vals)
            if count_item == resp_json['count']:
                has_next_page = False
        if resp:
            product_id.act_sync()
    
    @api.model
    def _check_sku_tada(self, vals):
        tada_id = self.env['tada.tada'].browse(vals['tada_id'])
        tada_id.check_token_validity()
        access_token = tada_id.access_token
        base_api_url = self.env['ir.config_parameter'].sudo().get_param('tada.base_api_url')
        authorization = 'Bearer {}'.format(access_token)
        headers = Headers.copy()
        headers['Authorization'] = authorization
        response = requests.get(base_api_url + ValidateSkuUrl.format(itemid=1, sku=vals['sku']), params=params, headers=headers, timeout=50.0)
        return
    
    @api.model
    def create(self, vals):
        # self._check_sku_tada(vals)
        res = super(TadaProduct, self).create(vals)
        if not self._context.get('sync', False):
            stock_id = self.env['tada.stock'].create({'name': res.name, 'quantity': res.quantity, 'product_id': res.id, 'price': res.price})
            res._create_to_tada(vals, stock_id)
        return res
    
    def write(self, vals):
        res = super(TadaProduct, self).write(vals)
        if not self._context.get('sync', False):
            self._update_to_tada(vals)
        return res
    
    def _create_to_tada(self, vals, stock_id):
        self.tada_id.check_token_validity()
        access_token = self.tada_id.access_token
        catalogCategoryIds = [self.env.ref('tada.tada_catalog_id').value]
        base_api_url = self.env['ir.config_parameter'].sudo().get_param('tada.base_api_url')
        authorization = 'Bearer {}'.format(access_token)
        headers = Headers.copy()
        headers['Authorization'] = authorization
        programid = self.env['ir.config_parameter'].sudo().get_param('tada.program_id')
        body = {'itemType': 'item',
                'programId': programid,
                'name': self.name,
                'image': self.image or None,
                'description': self.description,
                'CategoryId': str(self.category_id.categid),
                'catalogCategoryIds': catalogCategoryIds,
                'isLimited': self.is_limited,
                'active': self.active,
                'initialVariant': {"name": self.name, 
                                   "description": self.description, 
                                   "price": self.price, 
                                   "sku": self.sku, 
                                   "StockId": stock_id.stockid},}
        response = requests.post(base_api_url + ProductUrl, headers=headers, json=body, timeout=50.0)
        resp_json = response.json()
        if response.status_code != 201:
            raise ValidationError(_('Please Try Again Later'))
        resp_vals = {'productid': resp_json['id'],
                     'updatedAt': resp_json['updatedAt'],
                     'createdAt': resp_json['createdAt']
                     }
        self.with_context(sync=True).write(resp_vals)
        self.act_sync()
    
    def _update_to_tada(self, vals):
        if self.productid == 0:
            return
        updated_fields = set(vals.keys())
        difference_field = updated_fields.difference(TadaProductFields)
        for field in difference_field:
            vals.pop(field)
        if len(vals) == 0:
            return
        body = {TadaProductFieldsName[key]: value for key, value in vals.items()}
        category_id = self.category_id.browse(vals.get('category_id', self.category_id.id))
        catalogCategoryIds = [self.env.ref('tada.tada_catalog_id').value]
        body.update({'CategoryId': category_id.categid, 'catalogCategoryIds': catalogCategoryIds})
        body.update(name=vals.get('name', self.name))
        bodyJson = json.dumps(body)
        base_api_url = self.env['ir.config_parameter'].sudo().get_param('tada.base_api_url')
        self.tada_id.check_token_validity()
        access_token = self.tada_id.access_token
        authorization = 'Bearer {}'.format(access_token)
        headers = Headers.copy()
        headers['Authorization'] = authorization
        response = requests.put(base_api_url + ProductDetailUrl.format(itemid=self.productid), headers=headers, data=bodyJson, timeout=50.0)
        resp_json = response.json()
        if response.status_code != 200 or len(resp_json.get('failed', [])) != 0:
            if 'message' in resp_json:
                message = resp_json['message']
            elif 'failed' in resp_json:
                message = resp_json['failed'][0]['message']
            else:
                message = 'Error'
            raise ValidationError(_(message))
        self.with_context(sync=True).write({'updatedAt': resp_json['updatedAt']})
        return
    
    
class TadaProductVariant(models.Model):
    _name = 'tada.product.variant'
    _description = 'Tada Products Variant'
    
    tada_id = fields.Many2one('tada.tada', 'Tada', related='product_id.tada_id', store=True, index=True)
    product_id = fields.Many2one('tada.product', 'Product Item', ondelete="cascade", required=True, index=True) #itemid
    variantid = fields.Integer(readonly=True) # id
    name = fields.Char('Variant Name', required=True) # name
    description = fields.Html() # description
    image = fields.Char() # image
    sku = fields.Char('SKU', required=True) # sku
    value_type = fields.Char() # valueType
    min_price = fields.Integer() # minPrice
    is_multi_price = fields.Boolean() # isMultiPrice
    price = fields.Integer(default=0, required=False) # price
    source_type = fields.Char() # sourceType
    active = fields.Boolean(default=True) # active
    createdAt = fields.Datetime(readonly=True) # createdAt
    updatedAt = fields.Datetime(readonly=True) # updatedAt
    stock_id = fields.Many2one('tada.stock', 'Stocks', required=False, index=True) # StockId
    image_view = fields.Char(related='image')
    system_product_ids = fields.Many2many('product.product', string='Products on System', compute='_compute_system_product')
    quantity = fields.Integer(related='stock_id.quantity', default=0, required=True, store=True)
    bundling_quantity_ids = fields.One2many('tada.product.bundling.quantity', 'product_variant_id', 'Bundling Quantity')
    
    @api.constrains('sku')
    def _check_sku(self):
        variant_sku = self.search([('sku', '=', self.sku), ('tada_id', '=', self.tada_id.id)], limit=1)
        if variant_sku.id and variant_sku.id != self.id and not self._context.get('sync', False):
            raise ValidationError(_('SKU has been exist'))
    
    @api.depends('sku')
    def _compute_system_product(self):
        Product = self.env['product.product']
        for rec in self:
            if not rec.sku:
                continue
            sku_lst = rec.sku.split(';')
            if len(sku_lst) == 1:
                operator = '='
                sku = sku_lst[0]
            else:
                operator = 'in'
                sku = sku_lst
            
            system_product_ids = Product.search([('barcode', operator, sku)])
            rec.system_product_ids = [(6,0,system_product_ids.ids)]
        return
    
    def _create_to_tada(self, vals):
        self.tada_id.check_token_validity()
        access_token = self.tada_id.access_token
        base_api_url = self.env['ir.config_parameter'].sudo().get_param('tada.base_api_url')
        authorization = 'Bearer {}'.format(access_token)
        headers = Headers.copy()
        headers['Authorization'] = authorization
        body = {'name': self.name,
               "description": self.description, 
               "price": self.price, 
               "sku": self.sku,
               "StockId": self.stock_id.stockid}
        response = requests.post(base_api_url + VariantUrl, headers=headers, json=body, timeout=50.0)
        resp_json = response.json()
        resp_vals = self._convert_resp_tada_to_vals(self.tada_id, resp_json)
        return self.with_context(sync=True).write(resp_vals)
    
    def _update_to_tada(self, vals):
        updated_fields = set(vals.keys())
        difference_field = updated_fields.difference(TadaVariantFields)
        for field in difference_field:
            vals.pop(field)
        if len(vals) == 0:
            return
        body = {TadaVariantFieldsName[key]: value for key, value in vals.items()}
        body.update(name=vals.get('name', self.name), price=vals.get('price', self.price))
        bodyJson = json.dumps(body)
        base_api_url = self.env['ir.config_parameter'].sudo().get_param('tada.base_api_url')
        self.tada_id.check_token_validity()
        access_token = self.tada_id.access_token
        authorization = 'Bearer {}'.format(access_token)
        headers = Headers.copy()
        headers['Authorization'] = authorization
        response = requests.put(base_api_url + VariantDetailUrl.format(itemid=self.product_id.productid, variantId=self.variantid), headers=headers, data=bodyJson, timeout=50.0)
        resp_json = response.json()
        if response.status_code != 200 or len(resp_json.get('failed', [])) != 0:
            if 'message' in resp_json:
                message = resp_json['message']
            elif 'failed' in resp_json:
                message = resp_json['failed'][0]['message']
            else:
                message = 'Error'
            raise ValidationError(_(message))
        self.with_context(sync=True).write({'updatedAt': resp_json['updatedAt']})
    
    @api.model
    def _convert_resp_tada_to_vals(self, resp_dict, stocks=False):
        Stock = self.env['tada.stock']
        if not stocks:
            self._cr.execute('select id, stockid from %s' %(Stock._table))
            stocks = {stockid: id for id, stockid in self._cr.fetchall()}
        variant = resp_dict
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
        quantity = 0
        if resp_dict.get('Stock'):
            quantity = resp_dict['Stock'].get('quantity',0)
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
                        'quantity': quantity,
                        }
        stock = variant['Stock']
        if stock:
            stockid = stock['id']
            stock_id = stocks.get(stockid, False)
            if not stock_id:
                stock_vals = Stock._convert_resp_tada_to_vals(stock)
                stock_id = Stock.browse(stocks.get(stockid, False))
                if stock_id.id:
                    stock_id.write(stock_vals)
                else:
                    stock_id = Stock.create(stock_vals).id
                stocks.update({stockid: stock_id})
            variant_vals['stock_id'] = stock_id
        return variant_vals
    
    def act_sync(self):
        self = self.with_context(sync=True)
        Stock = self.env['tada.stock']
        # Category = self.env['tada.category']
        Product = self.env['tada.product']
        product_id = self.product_id
        tada_id = product_id.tada_id
        if not tada_id :
            return False
        self._cr.execute('select id, variantid from %s where product_id=%d' %(self._table, product_id.id))
        variants = {variantid: id for id, variantid in self._cr.fetchall()}
        self._cr.execute('select id, stockid from %s' %(Stock._table))
        stocks = {stockid: id for id, stockid in self._cr.fetchall()}
        base_api_url = self.env['ir.config_parameter'].sudo().get_param('tada.base_api_url')
        tada_id.check_token_validity()
        access_token = tada_id.access_token
        authorization = 'Bearer {}'.format(access_token)
        headers = Headers.copy()
        headers['Authorization'] = authorization
        response = requests.get(base_api_url + VariantDetailUrl.format(itemid=product_id.productid, variantId=self.variantid), headers=headers, timeout=50.0)
        resp_json = response.json()
        if response.status_code != 200 or len(resp_json.get('failed', [])) != 0:
            if 'message' in resp_json:
                message = resp_json['message']
            elif 'failed' in resp_json:
                message = resp_json['failed'][0]['message']
            else:
                message = 'Error'
            raise ValidationError(_(message))
        variant_vals = self._convert_resp_tada_to_vals(resp_json, stocks)
        self.write(variant_vals)
        return
    
    @api.model
    def create(self, vals):
        res = super(TadaProductVariant, self).create(vals)
        if not self._context.get('sync', False):
            res._create_to_tada(vals)
        return res
    
    def write(self, vals):
        res = super(TadaProductVariant, self).write(vals)
        if not self._context.get('sync', False):
            self._update_to_tada(vals)
        return res
      
            
class TadaProductBundlingQuantity(models.Model):
    _name = 'tada.product.bundling.quantity'
    _description = 'Product Bundling'
    
    product_variant_id = fields.Many2one('tada.product.variant', 'Product Variant', required=True)
    product_id = fields.Many2one('tada.product', 'Product', related='product_variant_id.product_id')
    system_product_id = fields.Many2one('product.product', 'System Product', required=True)
    quantity = fields.Float('Quantity')
    
    