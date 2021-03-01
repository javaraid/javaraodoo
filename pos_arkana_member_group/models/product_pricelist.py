from odoo import api, fields, models


class Pricelist(models.Model):
    _inherit = 'product.pricelist'

    is_member = fields.Boolean(string='Pricelist Member',default= False)