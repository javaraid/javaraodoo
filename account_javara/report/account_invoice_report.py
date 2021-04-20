# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models, fields, api

class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    invoice_id = fields.Many2one('account.invoice', 'Invoice Number', ondelete='cascade')
    origin = fields.Char('Source Document', readonly=True)
    price_with_tax = fields.Float(string='Total With Tax', readonly=True)
    total_without_discount = fields.Float('Total w/o Discount', digits=(16, 2), readonly=True, group_operator="sum")
    total_discount = fields.Float('Total Discount', digits=(16, 2), readonly=True, group_operator="sum")

    def _select(self):
        return super(AccountInvoiceReport, self)._select() + """
        , sub.invoice_id as invoice_id, 
        sub.origin as origin,
        sub.price_with_tax as price_with_tax, 
        sub.price_total + sub.discount as total_without_discount,
        sub.discount as total_discount
        """

    def _sub_select(self):
        return super(AccountInvoiceReport, self)._sub_select() + """
        , ai.id AS invoice_id, 
        ai.origin AS origin, 
        SUM(ail.price_total_signed) AS price_with_tax, 
        sum(ail.price_unit * (ail.discount / 100.0)) as discount
        """

    def _group_by(self):
        return super(AccountInvoiceReport, self)._group_by() + ", ai.id, ai.origin"

