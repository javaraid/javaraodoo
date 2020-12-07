# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    # rename Commercial Entity to match with Invoice Analysis
    commercial_partner_id = fields.Many2one('res.partner', 'Partner Company', readonly=True)
    
    delay_real = fields.Float('Avg. Days to Deliver', digits=(16, 2), readonly=True, group_operator="avg")
    invoiced_amount_percentage = fields.Float('% SL Invoiced vs Total', digits=(16, 2), readonly=True, group_operator="avg")
    invoiced_qty_percentage = fields.Float('% SL Qty Invoiced vs Ordered', digits=(16, 2), readonly=True, group_operator="avg")
    delivered_qty_percentage = fields.Float('% SL Qty Delivered vs Ordered', digits=(16, 2), readonly=True, group_operator="avg")

    amt_invoiced_untax = fields.Float('Amount Invoiced Untaxed', readonly=True)

    def _select(self):
        return super(SaleReport, self)._select() + \
        """, 
        extract(epoch from age(s.delivered_at,s.confirmation_date))/(24*60*60)::decimal(16,2) as delay_real, 
        sum(l.amt_invoiced_untax / COALESCE(cr.rate, 1.0)) as amt_invoiced_untax,
        SUM((l.amt_invoiced_untax / COALESCE(cr.rate, 1.0)) / (COALESCE(l.price_subtotal, 1.0) / COALESCE(cr.rate, 1.0)) * 100) as invoiced_amount_percentage,
        sum((l.qty_invoiced / u.factor * u2.factor) / (COALESCE(l.product_uom_qty / u.factor * u2.factor, 1.0)) * 100) as invoiced_qty_percentage,
        sum((l.qty_delivered / u.factor * u2.factor) / (COALESCE(l.product_uom_qty / u.factor * u2.factor, 1.0)) * 100) as delivered_qty_percentage
        """

    def _group_by(self):
        return super(SaleReport, self)._group_by() + ", s.delivered_at"