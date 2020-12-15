from odoo import models, fields, api, _
from odoo.tools.float_utils import float_compare, float_round, float_is_zero
from odoo.exceptions import UserError
from datetime import datetime
import pytz

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        if not self.product_uom or not self.product_id:
            self.price_unit = 0.0
            return
    
    amt_invoiced_untax = fields.Monetary(string='Amount Invoiced Untax', compute='_compute_invoice_amount', compute_sudo=True, store=True)

    @api.depends('state',
                 'price_reduce_taxinc',
                 'qty_delivered',
                 'invoice_lines',
                 'invoice_lines.price_total',
                 'invoice_lines.invoice_id',
                 'invoice_lines.invoice_id.state',
                 'invoice_lines.invoice_id.refund_invoice_ids',
                 'invoice_lines.invoice_id.refund_invoice_ids.state',
                 'invoice_lines.invoice_id.refund_invoice_ids.amount_total')
    def _compute_invoice_amount(self):
        for line in self:
            # Invoice lines referenced by this line
            invoice_lines = line.invoice_lines.filtered(lambda l: l.invoice_id.state in ('open', 'paid'))
            # Refund invoices linked to invoice_lines
            refund_invoices = invoice_lines.mapped('invoice_id.refund_invoice_ids').filtered(lambda inv: inv.state in ('open', 'paid'))
            refund_invoice_lines = refund_invoices.mapped('invoice_line_ids').filtered(lambda l: l.product_id == line.product_id)
            # If the currency of the invoice differs from the sale order, we need to convert the values
            if line.invoice_lines and line.invoice_lines[0].currency_id \
                    and line.invoice_lines[0].currency_id != line.currency_id:
                invoiced_amount_total = sum([inv_line.currency_id.with_context({'date': inv_line.invoice_id.date}).compute(inv_line.price_total, line.currency_id)
                                             for inv_line in invoice_lines])
                refund_amount_total = sum([inv_line.currency_id.with_context({'date': inv_line.invoice_id.date}).compute(inv_line.price_total, line.currency_id)
                                           for inv_line in refund_invoice_lines])
                invoiced_amount_untax = sum([inv_line.currency_id.with_context({'date': inv_line.invoice_id.date}).compute(inv_line.price_subtotal, line.currency_id)
                                             for inv_line in invoice_lines])
                refund_amount_untax = sum([inv_line.currency_id.with_context({'date': inv_line.invoice_id.date}).compute(inv_line.price_subtotal, line.currency_id)
                                           for inv_line in refund_invoice_lines])
            else:
                invoiced_amount_total = sum(invoice_lines.mapped('price_total'))
                refund_amount_total = sum(refund_invoice_lines.mapped('price_total'))
                invoiced_amount_untax = sum(invoice_lines.mapped('price_subtotal'))
                refund_amount_untax = sum(refund_invoice_lines.mapped('price_subtotal'))
            # Total of remaining amount to invoice on the sale ordered (and draft invoice included) to support upsell (when
            # delivered quantity is higher than ordered one). Draft invoice are ignored on purpose, the 'to invoice' should
            # come only from the SO lines.
            total_sale_line = line.price_total
            if line.product_id.invoice_policy == 'delivery':
                total_sale_line = line.price_reduce_taxinc * line.qty_delivered

            line.amt_invoiced = invoiced_amount_total - refund_amount_total
            line.amt_to_invoice = (total_sale_line - invoiced_amount_total) if line.state in ['sale', 'done'] else 0.0
            line.amt_invoiced_untax = invoiced_amount_untax - refund_amount_untax


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def _set_commitment_date(self):
        for rec in self :
            for pick in rec.picking_ids :
                pick.scheduled_date = rec.commitment_date

    delivery_status = fields.Selection([
            ('no', 'Not Delivered'),
            ('partial', 'Partially Delivered'),
            ('delivered', 'Fully Delivered')
        ], string='Delivery State', compute='_get_delivery', store='True')
    
    delivered_at = fields.Datetime('Delivered at', compute='_get_delivery', store='True')
    commitment_date = fields.Datetime(inverse='_set_commitment_date')

    @api.multi
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for rec in self :
            for pick in rec.picking_ids :
                if pick.scheduled_date != rec.commitment_date :
                    pick.scheduled_date = rec.commitment_date
        return res
    
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

    def get_commitment_date(self):
        self.ensure_one()
        if not self.commitment_date :
            return ''
        return pytz.UTC.localize(datetime.strptime(self.commitment_date, '%Y-%m-%d %H:%M:%S')).astimezone(pytz.timezone(self.env.user.tz or 'Asia/Jakarta')).strftime('%Y-%m-%d %H:%M:%S')

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

