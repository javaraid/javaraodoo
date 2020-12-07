# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models, fields, api

class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    price_with_tax = fields.Float(string='Total With Tax', readonly=True)

    invoice_id = fields.Many2one('account.invoice', 'Invoice Number', ondelete='cascade')

    origin = fields.Char('Source Document', readonly=True)
    total_without_discount = fields.Float('Total w/o Discount', digits=(16, 2), readonly=True, group_operator="sum")
    total_discount = fields.Float('Total Discount', digits=(16, 2), readonly=True, group_operator="sum")

    # def _from(self):
    #     return super(AccountInvoiceReport, self)._from() + """
    #     JOIN (
    #         -- Temporary table to decide if the value should be added or retrieved (Invoice vs Credit Note)
    #         SELECT id,(CASE
    #                 WHEN ai.type::text = ANY (ARRAY['out_refund'::character varying::text, 'in_invoice'::character varying::text])
    #                 THEN -1
    #                 ELSE 1
    #             END) AS sign
    #         FROM account_invoice ai
    #     ) AS invoice_type_total ON invoice_type_total.id = ai.id
    #     """

    def _select(self):
        return super(AccountInvoiceReport, self)._select() + """
        , sub.invoice_id as invoice_id, sub.price_with_tax as price_with_tax, sub.origin as origin,
        (sub.price_subtotal / COALESCE(cr.rate, 1.0)) + ((sub.price_unit / COALESCE(cr.rate, 1.0)) * sub.discount / 100) * (COALESCE(sub.product_qty, 1.0)) as total_without_discount,
        ((sub.price_unit / COALESCE(cr.rate, 1.0)) * sub.discount / 100) * (COALESCE(sub.product_qty, 1.0)) as total_discount
        """

    def _sub_select(self):
        return super(AccountInvoiceReport, self)._sub_select() + """
        , ai.id AS invoice_id, SUM(ail.price_total_signed * invoice_type.sign) AS price_with_tax, ai.origin AS origin, 
        sum(ail.price_subtotal) as price_subtotal, 
        sum(ail.price_unit) as price_unit, 
        sum(ail.discount) as discount
        """

    def _group_by(self):
        return super(AccountInvoiceReport, self)._group_by() + ", ai.id, ai.origin"

