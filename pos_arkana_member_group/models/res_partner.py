from odoo import api, fields, models


class Partner(models.Model):
    _inherit = 'res.partner'
    
    # karena 1 partner 1 member group dan bisa di active nonactive
    @api.depends('partner_member_detail_ids')
    def _compute_active_member(self):
        for record in self:
            if record.partner_member_detail_ids:
                member = record.partner_member_detail_ids[0]
                record.active_member_id = member.partner_member_id.id # ambil satu
                record.property_product_pricelist = member.partner_member_id.pricelist_id and member.partner_member_id.pricelist_id.id or False

    active_member_id = fields.Many2one(comodel_name='res.partner.member',
        string='Active Group Member', compute='_compute_active_member', store=True,)
    partner_member_detail_ids = fields.One2many(comodel_name='res.partner.member.detail', 
        inverse_name='partner_id', string='Member Details')
    
    