from odoo import models, fields, api


class CrmTeam(models.Model):
    _inherit = 'crm.team'
    
    team_type = fields.Selection(selection_add=[('tada', 'Tada')])
    

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_from_tada = fields.Boolean('From Tada')
    tada_order_ids = fields.One2many('tada.order', 'sale_order_id', 'Order')
    purchase_number_tada = fields.Char(
        string='Purchase Order Number',
        readonly=False,
        copy=False)
    
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for rec in self :
            if rec.is_from_tada:
                rec.tada_order_ids.filtered(lambda order: order.status != 'on process').action_confirm()
                rec.picking_ids.write({'is_request_pickup': self.tada_order_ids[:1].is_request_pickup})
        return res
