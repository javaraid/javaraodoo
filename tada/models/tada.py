import re
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from addons.event_sale.models.product import Product

def sync(fun):
    def wrapper(par):
        par = par.with_context(sync=True)
        return fun(par)
    return wrapper


class TadaTada(models.Model):
    _name = 'tada.tada'
    _description = 'Tada Account'
    _rec_name = 'username'
    
    name = fields.Char('Name')
    username = fields.Char('Username', required=True)
    access_token = fields.Char('Token')
    expired_at = fields.Datetime('Expired At', readonly=True)
    state = fields.Selection([('new', 'New'), ('establish', 'Established'), ('expired', 'Expired')], 'State', default='new')
    category_ids = fields.One2many('tada.category', 'tada_id', 'Categories')
    product_ids = fields.One2many('tada.product', 'tada_id', 'Products')
    # mId = fields.Char()
    order_ids = fields.One2many('tada.order', 'tada_id', 'Orders')
    
    @api.constrains('username')
    def _check_username(self):
        regex = r'[\w.-]+@[\w.-]+.\w+'
        if not re.search(regex,self.username):  
            raise ValidationError("Invalid Email")
    
    @api.model
    def _sync(self):
        tada_ids = self.search([('state', '=', 'establish')])
        for tada_id in tada_ids:
            tada_id.act_sync()
    
    def act_sync(self):
        self = self.with_context(sync=True)
        Category = self.env['tada.category']
        Product = self.env['tada.product']
        Order = self.env['tada.order']
        Category._get_on_tada(self.access_token)
        Product._get_on_tada(self.access_token)
        Order._get_on_tada(self.access_token)
    
    def act_sync_order(self):
        self = self.with_context(sync=True)
        Order = self.env['tada.order']
        Order._get_on_tada(self.access_token)
    
    @sync
    def act_sync_product(self):
        Product = self.env['tada.product']
        Product._get_on_tada(self.access_token)
        
    def act_sync_category(self):
        self = self.with_context(sync=True)
        Category = self.env['tada.category']
        Category._get_on_tada(self.access_token)


class TadaStore(models.Model):
    _name = 'tada.store'
    _description = 'Tada Store'
    
    name = fields.Char()
    tada_id = fields.Many2one('tada.tada', 'Tada', ondelete='cascade')
    
    
    