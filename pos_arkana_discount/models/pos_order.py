from odoo import api, fields, models


class PosOrderDiscount(models.Model):
    _inherit = 'pos.order'

    choose_disc = fields.Char(string='Choose Discount')
   
    disc_type = fields.Selection(string='Global Discount Type', 
        selection=[('fix', 'Fix'), ('percent', 'Percent'),],
        default=False,)
    global_disc = fields.Float(string='Global Discount', help="Dalam persen atau fixed")
    global_disc_amount = fields.Float(string='Global Discount Fixed', help="Dalam fixed", readonly=True,)

    @api.model
    def _order_fields(self, ui_order):
        fields = super(PosOrderDiscount, self)._order_fields(ui_order)
        fields['disc_type'] = ui_order.get('disc_type', False)
        fields['global_disc'] = ui_order.get('global_disc', 0.0)
        fields['global_disc_amount'] = ui_order.get('global_disc_amount', 0.0)
        return fields

class PosOrderLineDiscount(models.Model):
    _inherit = 'pos.order.line'

    global_disc_line = fields.Float(string='Global Disc Amount', default=0.0, readonly=True,)