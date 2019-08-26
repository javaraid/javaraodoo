from odoo import models, fields, api, _
from odoo.tools.float_utils import float_compare, float_round, float_is_zero
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        if not self.product_uom or not self.product_id:
            self.price_unit = 0.0
            return


class SaleTarget(models.Model):
    _name = 'sale.target'
    _description = 'Sales Target'

    name = fields.Char(string='Name')
    date_from = fields.Date(string='From')
    date_to = fields.Date(string='To')
    amount_actual = fields.Float(string='Actual', compute='_get_actual')
    amount_target = fields.Float(string='Target')
    percentage = fields.Float(string='(%)', compute='_get_actual')

    @api.multi
    @api.depends('date_from', 'date_to', 'amount_target')
    def _get_actual(self):
        for target in self:
            if target.date_from and target.date_to:
                domain = [
                    ('state', 'in', ['sale', 'done']),
                    ('confirmation_date', '>=', target.date_from),
                    ('confirmation_date', '<=', target.date_to),
                ]
                sales = self.env['sale.order'].search(domain)
                if sales:
                    amount_actual = sum(sales.mapped('amount_total'))
                    target.amount_actual = amount_actual

            amount_target = target.amount_target
            target.parcentage = amount_actual / amount_target if amount_target > 0 else 0


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    delivery_state = fields.Selection([
            ('no', 'Not Delivered'),
            ('partial', 'Partially Delivered'),
            ('delivered', 'Fully Delivered')
        ], string='Delivery State', compute='_get_delivery', store='True')
    
    @api.depends('state', 'picking_ids.state')
    def _get_delivery(self):
        for order in self:
            if order.state not in ('sale', 'done'):
                delivery_state = 'no'
            elif all(picking.state != 'done' for picking in order.picking_ids):
                delivery_state = 'no'
            elif all(picking.state in ('done', 'cancel') for picking in order.picking_ids):
                delivery_state = 'delivered'
            else:
                delivery_state = 'partial'

            order.update({
                'delivery_state': delivery_state
            })