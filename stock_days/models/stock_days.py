# from odoo import models, fields, api, _
# from odoo.tools.float_utils import float_compare, float_round, float_is_zero
# from odoo.exceptions import UserError
from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from odoo.tools import float_compare
from datetime import datetime


class Picking(models.Model):
    _inherit = "stock.picking"

    done_at = fields.Datetime('Done At')
    days = fields.Integer(string='Days to Delivery')

    # Days to Deliver is duration creation date (order confirmation date) until validate date
    # if the picking is a backorder, the ancestor creation date become the
    # base date
    @api.multi
    @api.depends('create_date', 'done_at')
    def button_validate(self):
        res = super(Picking, self).button_validate()
        self.done_at = datetime.now()

        base_date = self.create_date
        current = self
        while current.backorder_id:
            base_date = current.backorder_id.create_date
            current = current.backorder_id

        from_date = datetime.strptime(str(base_date), '%Y-%m-%d %H:%M:%S')
        to_date = datetime.strptime(str(self.done_at), '%Y-%m-%d %H:%M:%S')
        timedelta = to_date - from_date
        diff_day = timedelta.days + float(timedelta.seconds) / 86400
        self.days = diff_day
        return res


class ReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    @api.model
    def default_get(self, fields):
        res = super(ReturnPicking, self).default_get(fields)
        for i in range(0, len(res['product_return_moves'])):
            res['product_return_moves'][i][2]['to_refund'] = True
        return res
