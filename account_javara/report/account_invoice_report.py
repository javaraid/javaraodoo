# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models, fields, api

class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    price_with_tax = fields.Float(string='Total With Tax', readonly=True)

    invoice_id = fields.Many2one('account.invoice', 'Invoice Number', ondelete='cascade')

    origin = fields.Char('Source Document', readonly=True)

    def _select(self):
        return super(AccountInvoiceReport, self)._select() + ", sub.invoice_id as invoice_id, sub.price_with_tax as price_with_tax, sub.origin as origin"

    def _sub_select(self):
        return super(AccountInvoiceReport, self)._sub_select() + ", ai.id AS invoice_id, SUM(ail.price_total_signed * invoice_type.sign) AS price_with_tax, ai.origin AS origin"

    def _group_by(self):
        return super(AccountInvoiceReport, self)._group_by() + ", ai.id, ai.origin"

