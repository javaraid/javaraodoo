from odoo import models, fields, api


class Picking(models.Model):
    _inherit = 'stock.picking'
    
    is_from_tada = fields.Boolean('Is Using External', compute='_compute_is_from_tada')
    tracking_number = fields.Char('Tracking Number')
    shipping_company_id = fields.Many2one('tada.shipping.company', 'Shipping Company')
    is_request_pickup = fields.Boolean('Is Request Pickup?')
    
    def action_done(self):
        res = super(Picking, self).action_done()
        for pick in self:
            sale_id = pick.sale_id
            is_from_tada = sale_id.is_from_tada
            tada_order_id = sale_id.tada_order_ids
            if is_from_tada and tada_order_id:
                tada_order_id.tracking_number = pick.tracking_number
                tada_order_id.shipping_company_id = pick.shipping_company_id.id
                tada_order_id.action_process()
    
    def _compute_is_from_tada(self):
        for rec in self:
            rec.is_from_tada = rec.sale_id.is_from_tada
        return
    
    def action_request_pickup(self):
        tada_order_id = self.sale_id.tada_order_ids
        tada_order_id.action_request_pickup()
        return
    
    