from odoo import api, fields, models, _

class PosOrderReport(models.Model):
    _inherit = 'report.pos.order'

    tender_type_id = fields.Many2one(
        comodel_name='pos.tender.type',
        string='Tender Type',
        required=False)
    payment_journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Payment Method',
        store=True)

    def _select(self):
        res = super(PosOrderReport, self)._select()
        res += ', s.tender_type_id, s.payment_journal_id '
        return res

    def _group_by(self):
        res = super(PosOrderReport, self)._group_by()
        res += ', s.tender_type_id, s.payment_journal_id '
        return res
