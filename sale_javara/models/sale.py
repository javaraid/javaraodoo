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

    @api.multi
    def write(self, values):
        res = super(SaleOrder, self).write(values)
        if values.get('note') and not self._context.get('force_write'):
            for rec in self :
                rec.invoice_ids.with_context({'force_write':True}).write({'comment':values['note']})
        return res

    def get_commitment_date(self):
        self.ensure_one()
        if not self.commitment_date :
            return ''
        return pytz.UTC.localize(datetime.strptime(self.commitment_date, '%Y-%m-%d %H:%M:%S')).astimezone(pytz.timezone(self.env.user.tz or 'Asia/Jakarta')).strftime('%Y-%m-%d %H:%M:%S')

class SaleTarget(models.Model):
    _name = 'sale.target'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = 'Sales Target'
    _order = 'id desc'

    name = fields.Char(string='Name', default='New')
    date_from = fields.Date(string='From', required=True)
    date_to = fields.Date(string='To', required=True)
    amount_actual = fields.Float(string='Actual Amount', compute='_get_actual', store=True)
    amount_target = fields.Float(string='Targeted Amount')
    amount_invoiced = fields.Float(string='Invoiced Amount', compute='_get_actual', store=True)
    percentage_amount = fields.Float(string='Accomplished Amount (%)', compute='_get_actual', store=True, group_operator="avg")
    unselected_salesperson = fields.Boolean(
        string='Unselected Salesperson',
        help='All unselected salesperson in other records for the same period',
        required=False)
    salesperson_id = fields.Many2one('res.users', 'Salesperson', ondelete='set null')
    unselected_saleschannel = fields.Boolean(
        string='Unselected Sales Channel',
        help='All unselected sales channel in other records for the same period',
        required=False)
    saleschannel_id = fields.Many2one('crm.team', 'Sales Channel', ondelete='set null')
    company_id = fields.Many2one('res.company', 'Company', ondelete='cascade')
    unselected_customer = fields.Boolean(
        string='Unselected Customer',
        help='All unselected customer in other records for the same period',
        required=False)
    customer_id = fields.Many2one('res.partner', 'Customer', ondelete='cascade')
    unselected_product = fields.Boolean(
        string='Unselected Product',
        help='All unselected product in other records for the same period',
        required=False)
    product_id = fields.Many2one('product.product', 'Product', ondelete='cascade')
    qty_target = fields.Float(string='Target Qty')
    qty_actual = fields.Float(string='Actual Qty', compute='_get_actual', store=True)
    qty_invoiced = fields.Float(string='Invoiced Qty', compute='_get_actual', store=True)
    percentage_qty = fields.Float(string='Accomplished Qty (%)', compute='_get_actual', store=True, group_operator="avg")
    amt_invoiced_vs_amt_target = fields.Float(string='Invoiced Amount vs Target Amount (%)', compute='_get_actual', store=True, group_operator="avg")
    qty_invoiced_vs_amt_target = fields.Float(string='Invoiced Qty vs Target Qty (%)', compute='_get_actual', store=True, group_operator="avg")

    @api.model
    def create(self, values):
        if values.get('name', 'New') == 'New' :
            values['name'] = self.sudo().env['ir.sequence'].next_by_code('sale.target')
        return super(SaleTarget, self).create(values)

    @api.onchange('unselected_salesperson','unselected_saleschannel','unselected_customer','unselected_product')
    def onchange_set_null(self):
        if self.unselected_salesperson :
            self.salesperson_id = False
        if self.unselected_saleschannel :
            self.saleschannel_id = False
        if self.unselected_customer :
            self.customer_id = False
        if self.unselected_product :
            self.product_id = False

    def get_same_period(self, target, field):
        domain = [
            ('date_from','=',target.date_from),
            ('date_to','=',target.date_to),
        ]
        if isinstance(target.id, int) :
            domain.append(('id','!=',target.id))
        other_targets = self.search(domain)
        return other_targets.mapped(field)

    @api.multi
    @api.depends('date_from', 'date_to', 'amount_target', 'salesperson_id', 'saleschannel_id',
                 'company_id', 'customer_id', 'product_id', 'qty_target', 'unselected_saleschannel',
                 'unselected_salesperson', 'unselected_customer', 'unselected_product')
    def _get_actual(self):
        for target in self:
            amt_invoiced_vs_amt_target = 0
            qty_invoiced_vs_amt_target = 0
            if target.date_from and target.date_to:
                domain = [
                    ('state', 'in', ['sale', 'done']),
                    ('confirmation_date', '>=', target.date_from),
                    ('confirmation_date', '<=', target.date_to),
                ]

                if target.unselected_salesperson :
                    other_sales_person = self.get_same_period(target=target, field='salesperson_id')
                    if other_sales_person :
                        domain.append(('user_id', 'not in', other_sales_person.ids))
                elif target.salesperson_id :
                    domain.append(('user_id','=',target.salesperson_id.id))

                if target.unselected_saleschannel :
                    other_sales_channel = self.get_same_period(target=target, field='saleschannel_id')
                    if other_sales_channel :
                        domain.append(('team_id', 'not in', other_sales_channel.ids))
                elif target.saleschannel_id :
                    domain.append(('team_id','=',target.saleschannel_id.id))

                if target.company_id :
                    domain.append(('company_id','=',target.company_id.id))

                if target.unselected_customer :
                    other_customer = self.get_same_period(target=target, field='customer_id')
                    if other_customer :
                        domain += [
                            ('partner_id', 'not in', other_customer.ids),
                            ('partner_id.parent_id', 'not in', other_customer.ids),
                        ]
                elif target.customer_id :
                    if target.customer_id.child_ids:
                        domain.append(('partner_id.parent_id','=',target.customer_id.id))
                    else:
                        domain.append(('partner_id','=',target.customer_id.id))

                sales = self.env['sale.order'].search(domain)
                order_lines = sales.mapped('order_line')
                if order_lines:
                    if target.unselected_product or target.product_id :
                        line_domain = [('order_id', 'in', sales.ids)]
                        if target.unselected_product:
                            other_product = self.get_same_period(target=target, field='product_id')
                            if other_product:
                                line_domain.append(('product_id', 'not in', other_product.ids))
                        elif target.product_id:
                            line_domain.append(('product_id', '=', target.product_id.id))
                        order_lines = self.env['sale.order.line'].search(line_domain)
                        amount_actual = sum(order_lines.mapped(lambda l: l.product_uom_qty * l.price_unit))
                        target.amount_actual = amount_actual
                        amount_invoiced = sum(order_lines.mapped(lambda l: l.amt_invoiced))
                        target.amount_invoiced = amount_invoiced
                        qty_actual = sum(order_lines.mapped(lambda l: l.product_uom_qty))
                        target.qty_actual = qty_actual
                    else:
                        amount_actual = sum(sales.mapped('amount_untaxed'))
                        target.amount_actual = amount_actual
                        amount_invoiced = sum(order_lines.mapped('amt_invoiced'))
                        target.amount_invoiced = amount_invoiced

                target.qty_invoiced = sum(order_lines.mapped('qty_invoiced'))
                amount_target = target.amount_target
                target.percentage_amount = target.amount_actual / amount_target * 100 if amount_target > 0 else 0
                target.percentage_qty = target.qty_actual / target.qty_target * 100 if target.qty_target > 0 else 0
                if target.amount_target :
                    amt_invoiced_vs_amt_target = target.amount_invoiced / target.amount_target * 100
                if target.qty_target :
                    qty_invoiced_vs_amt_target = target.qty_invoiced / target.qty_target * 100
                target.amt_invoiced_vs_amt_target = amt_invoiced_vs_amt_target
                target.qty_invoiced_vs_amt_target = qty_invoiced_vs_amt_target
