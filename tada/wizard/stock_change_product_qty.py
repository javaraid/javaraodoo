from odoo import models, fields, api


class ProductChangeQuantity(models.TransientModel):
    _inherit = "stock.change.product.qty"
    
    
    