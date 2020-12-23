from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class PosOrder(models.Model):
    _inherit = 'pos.order'

    tender_type_id = fields.Many2one(
        comodel_name='pos.tender.type',
        string='Tender Type',
        required=False)
