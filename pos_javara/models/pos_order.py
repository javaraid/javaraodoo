from odoo import fields, api, models, _

class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    price_subtotal = fields.Float(store=True)
