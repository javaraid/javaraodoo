from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    stock_rule = fields.Selection(
        string='Stock Rule',
        selection=[
            ('not_less', 'Can not Produce MO Less Than Stock'),
            ('less', 'Can Produce MO Less Than Stock'),
            ('less_approval', 'Can Produce MO Less Than Stock With Approval'),
        ], required=True, default='not_less')
