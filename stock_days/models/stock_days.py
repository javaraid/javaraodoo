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

    @api.multi
    @api.depends('create_date', 'done_at')
    def button_validate(self):
        self.done_at = datetime.now()
        self.write({'state': 'done'})
        from_date = datetime.strptime(str(self.create_date), '%Y-%m-%d %H:%M:%S')
        to_date = datetime.strptime(str(self.done_at), '%Y-%m-%d %H:%M:%S')
        timedelta = to_date - from_date
        diff_day = timedelta.days + float(timedelta.seconds) / 86400
        self.days = diff_day
        
            
