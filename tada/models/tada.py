import re
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class TadaTada(models.Model):
    _name = 'tada.tada'
    _description = 'Tada Account'
    _rec_name = 'username'
    
    name = fields.Char('Name')
    username = fields.Char('Username', required=True)
    access_token = fields.Char('Token')
    expired_at = fields.Datetime('Expired At')
    state = fields.Selection([('new', 'New'), ('establish', 'Established'), ('expired', 'Expired')], 'State', default='new')
    category_ids = fields.One2many('tada.category', 'tada_id', 'Category')
    product_ids = fields.One2many('tada.product', 'tada_id', 'Product')
    # mId = fields.Char()
    
    @api.constrains('username')
    def _check_username(self):
        regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
        if not re.search(regex,self.username):  
            raise ValidationError("Invalid Email")
    
    @api.model
    def _sync(self):
        tada_ids = self.search([('state', '=', 'establish')])
        for tada_id in tada_ids:
            tada_id.act_sync()
    
    def act_sync(self):
        self.category_ids._get_on_tada(self.access_token)
        self.product_ids._get_on_tada(self.access_token)
        

class TadaStore(models.Model):
    _name = 'tada.store'
    _description = 'Tada Store'
    
    name = fields.Char()
    tada_id = fields.Many2one('tada.tada', 'Tada', ondelete='cascade')
    
    
    