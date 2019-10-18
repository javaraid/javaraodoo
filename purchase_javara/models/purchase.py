from odoo import models, fields, api, _
from odoo.tools.float_utils import float_compare, float_round, float_is_zero
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'purchase.order'

    delivery_status = fields.Selection([
            ('no', 'Not Delivered'),
            ('partial', 'Partially Delivered'),
            ('delivered', 'Fully Delivered')
        ], string='Delivery State', compute='_get_delivery', store='True')
    
    @api.depends('state', 'picking_ids.state')
    def _get_delivery(self):
        for order in self:
            if order.state not in ('purchase', 'done'):
                delivery_state = 'no'
            elif all(picking.state != 'done' for picking in order.picking_ids):
                delivery_state = 'no'
            elif all(picking.state in ('done', 'cancel') for picking in order.picking_ids):
                delivery_state = 'delivered'
            else:
                delivery_state = 'partial'

            order.update({
                'delivery_status': delivery_state
            })