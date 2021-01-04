from odoo import models, fields, api


class Picking(models.Model):
    _inherit = 'stock.picking'
    
    def action_done(self):
        res = super(Picking, self).action_done()
        for pick in self:
            sale_id = pick.sale_id
            if sale_id.is_from_tada:
                tada_order_id = self.env['tada.order'].search([('sale_order_id', '=', sale_id.id)])
                tada_order_id.action_process()
    
    