from odoo import models, api, fields, _
from odoo.tools.misc import format_date
from dateutil.relativedelta import relativedelta


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    date_maturity_ttf = fields.Date(
        string='Date Maturity TTF', compute='_compute_date_maturity_ttf', store=True)
    team_id = fields.Many2one(string='Sales Channel', related='partner_id.team_id', store=True)

    @api.multi
    @api.depends('invoice_id', 'date_maturity', 'invoice_id.date_ttf', 'invoice_id.date_invoice')
    def _compute_date_maturity_ttf(self):
        for aml in self:
            if aml.invoice_id and aml.invoice_id.date_ttf:
                date_invoice_df = fields.Date.from_string(
                    aml.invoice_id.date_invoice)
                date_ttf_df = fields.Date.from_string(aml.invoice_id.date_ttf)
                diff = date_ttf_df - date_invoice_df
                date_maturity_df = fields.Date.from_string(aml.date_maturity)
                date_maturity_ttf_df = date_maturity_df + diff
                aml.date_maturity_ttf = fields.Date.to_string(date_maturity_ttf_df)


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    date_ttf = fields.Date(string='TTF')
