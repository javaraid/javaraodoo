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

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    delivery_status = fields.Selection([
            ('no', 'Not Delivered'),
            ('partial', 'Partially Delivered'),
            ('delivered', 'Fully Delivered')
        ], string='Delivery State', compute='_get_delivery', store='True')
    
    delivered_at = fields.Datetime('Delivered at', compute='_get_delivery', store='True')
    
    @api.depends('state', 'picking_ids.state')
    def _get_delivery(self):
        for order in self:
            delivered_at = False
            if order.state not in ('sale', 'done'):
                delivery_state = 'no'
            elif all(picking.state != 'done' for picking in order.picking_ids):
                delivery_state = 'no'
            elif all(picking.state in ('done', 'cancel') for picking in order.picking_ids):
                delivery_state = 'delivered'
                last_picking = order.picking_ids.filtered(lambda p: p.picking_type_code == 'outgoing').sorted(key=lambda p: p.create_date, reverse=True)[0] if order.picking_ids else False
                if last_picking:
                    delivered_at = last_picking.done_at or last_picking.x_studio_field_aixKm
            else:
                delivery_state = 'partial'

            order.update({
                'delivery_status': delivery_state,
                'delivered_at': delivered_at
            })

class SaleTarget(models.Model):
    _name = 'sale.target'
    _description = 'Sales Target'

    name = fields.Char(string='Name')
    date_from = fields.Date(string='From', required=True)
    date_to = fields.Date(string='To', required=True)
    amount_actual = fields.Float(string='Actual Amount', compute='_get_actual', store=True)
    amount_target = fields.Float(string='Targeted Amount')
    amount_invoiced = fields.Float(string='Invoiced Amount', compute='_get_actual', store=True)
    percentage_amount = fields.Float(string='Accomplished Amount (%)', compute='_get_actual', store=True)
    salesperson_id = fields.Many2one('res.users', 'Salesperson', ondelete='set null')
    saleschannel_id = fields.Many2one('crm.team', 'Sales Channel', ondelete='set null')
    company_id = fields.Many2one('res.company', 'Company', ondelete='cascade')
    customer_id = fields.Many2one('res.partner', 'Customer', ondelete='cascade')
    product_id = fields.Many2one('product.product', 'Product', ondelete='cascade')
    qty_target = fields.Integer(string='Target Qty')
    qty_actual = fields.Integer(string='Actual Qty', compute='_get_actual', store=True)
    percentage_qty = fields.Float(string='Accomplished Qty (%)', compute='_get_actual', store=True)

    @api.multi
    @api.depends('date_from', 'date_to', 'amount_target', 'salesperson_id', 'saleschannel_id', 'company_id', 'customer_id', 'product_id', 'qty_target')
    def _get_actual(self):
        for target in self:
            if target.amount_target <= 0 or (target.product_id and target.qty_target <= 0):
                continue
            else:
                if target.date_from and target.date_to:
                    domain = [
                        ('state', 'in', ['sale', 'done']),
                        ('confirmation_date', '>=', target.date_from),
                        ('confirmation_date', '<=', target.date_to),
                    ]
                    
                    if target.salesperson_id :
                        domain.append(('user_id','=',target.salesperson_id.id))

                    if target.saleschannel_id :
                        domain.append(('team_id','=',target.saleschannel_id.id))

                    if target.company_id :
                        domain.append(('company_id','=',target.company_id.id))
                    
                    if target.customer_id :
                        if target.customer_id.child_ids:
                            domain.append(('partner_id.parent_id','=',target.customer_id.id))
                        else:
                            domain.append(('partner_id','=',target.customer_id.id))

                    sales = self.env['sale.order'].search(domain)
                    order_lines = sales.mapped('order_line')
                    if sales: 
                        if target.product_id:
                            amount_actual = sum(order_lines.filtered(lambda l: l.product_id.id == target.product_id.id).mapped(lambda l: l.product_uom_qty * l.price_unit))
                            target.amount_actual = amount_actual
                            amount_invoiced = sum(order_lines.filtered(lambda l: l.product_id.id == target.product_id.id).mapped(lambda l: l.amt_invoiced))
                            target.amount_invoiced = amount_invoiced
                            qty_actual = sum(order_lines.filtered(lambda l: l.product_id.id == target.product_id.id).mapped(lambda l: l.product_uom_qty))
                            target.qty_actual = qty_actual
                        else:
                            amount_actual = sum(sales.mapped('amount_untaxed'))
                            target.amount_actual = amount_actual
                            amount_invoiced = sum(order_lines.mapped('amt_invoiced'))
                            target.amount_invoiced = amount_invoiced

                amount_target = target.amount_target
                target.percentage_amount = target.amount_actual / amount_target * 100 if amount_target > 0 else 0
                target.percentage_qty = target.qty_actual / target.qty_target * 100 if target.qty_target > 0 else 0

