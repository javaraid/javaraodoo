# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    # rename Commercial Entity to match with Invoice Analysis
    commercial_partner_id = fields.Many2one('res.partner', 'Partner Company', readonly=True)