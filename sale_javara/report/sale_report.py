# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    # rename Commercial Entity to match with Invoice Analysis
    commercial_partner_id = fields.Many2one('res.partner', 'Partner Company', readonly=True)
    
    delay_real = fields.Float('Avg. Days to Deliver', digits=(16, 2), readonly=True, group_operator="avg")

    def _select(self):
        return super(SaleReport, self)._select() + ", extract(epoch from age(s.delivered_at,s.confirmation_date))/(24*60*60)::decimal(16,2) as delay_real"

    def _group_by(self):
        return super(SaleReport, self)._group_by() + ", s.delivered_at"