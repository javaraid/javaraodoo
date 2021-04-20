from odoo import api, fields, models, tools


class PosOrderReport(models.Model):
    _inherit = 'report.pos.order'

    price_subtotal = fields.Float(digits=0, string='Subtotal w/o Tax')

    def _select(self):
        res = super(PosOrderReport, self)._select()
        res += ", SUM(l.price_subtotal) AS price_subtotal"
        return res

