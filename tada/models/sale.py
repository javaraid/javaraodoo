from odoo import models, fields, api


class CrmTeam(models.Model):
    _inherit = 'crm.team'
    
    team_type = fields.Selection(selection_add=[('tada', 'Tada')])
    

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_from_tada = fields.Boolean('From Tada')
    tada_order_ids = fields.One2many('tada.order', 'sale_order_id', 'Order')
    
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        if self.is_from_tada:
            self.tada_order_ids.action_confirm()
            self.picking_ids.is_request_pickup = self.tada_order_ids.is_request_pickup
        return res
    
    