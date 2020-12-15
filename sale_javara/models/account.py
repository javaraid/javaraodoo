from odoo import api, fields, models, _

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def write(self, values):
        res = super(AccountInvoice, self).write(values)
        if values.get('comment') and not self._context.get('force_write'):
            for rec in self:
                sale_ids = rec.mapped('invoice_line_ids.sale_line_ids.order_id')
                sale_ids.with_context({'force_write':True}).write({'note': values['comment']})
        return res
