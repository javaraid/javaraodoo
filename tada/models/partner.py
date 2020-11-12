from odoo import models, fields, api


class Partner(models.Model):
    _inherit = 'res.partner'
    
    tadaid = fields.Integer()
    
    