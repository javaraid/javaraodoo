from odoo import models, api, fields, _
from odoo.tools.misc import format_date
from dateutil.relativedelta import relativedelta


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    date_maturity_ttf = fields.Date(
        string='Date Maturity TTF', compute='_compute_date_maturity_ttf', store=True)
    team_id = fields.Many2one(string='Sales Channel',
                              related='partner_id.team_id', store=True)

#     saleschannel_id = fields.Many2one('crm.team','Sales Channel',
#                               compute='_compute_saleschannel', store=True)

    # to add saleschannel in PoS transactions
    # used in reporting
#     @api.multi
#     @api.depends('partner_id.team_id', 'ref')
#     def _compute_saleschannel(self):
#         for record in self:
#             if record.partner_id and record.partner_id.team_id:
#                 record.saleschannel_id = record.partner_id.team_id
#             elif not record.partner_id and record.journal_id.type == 'sale' and 'POS' in record.ref:
#                 record.saleschannel_id = self.env['pos.session'].search([('name','=', record.ref)])[0].crm_team_id
#             else:
#                 continue

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
                aml.date_maturity_ttf = fields.Date.to_string(
                    date_maturity_ttf_df)


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    date_ttf = fields.Date(string='Date TTF')
