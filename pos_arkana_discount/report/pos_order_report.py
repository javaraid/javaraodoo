from odoo import api, fields, models, tools

class PosOrderReportInherit(models.Model):
    _inherit ='report.pos.order'

    def _select(self):
        select = super(PosOrderReportInherit, self)._select()
        new_select = select.replace(
                "SUM((l.qty * l.price_unit) * (100 - l.discount) / 100) AS price_total",
                "SUM(((l.qty * l.price_unit) - (l.global_disc_line + l.bank_disc_line)) * (100 - l.discount) / 100) AS price_total"
            )
        new_select = new_select.replace(
                "SUM((l.qty * l.price_unit) * (l.discount / 100)) AS total_discount",
                "SUM((l.qty * l.price_unit) - (((l.qty * l.price_unit) - (l.global_disc_line + l.bank_disc_line)) * (100 - l.discount) / 100)) AS total_discount"
            )
        return new_select