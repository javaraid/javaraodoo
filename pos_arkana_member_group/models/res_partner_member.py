from odoo import api, fields, models,_
from odoo.exceptions import ValidationError

class ResPartnerMemberInherit(models.Model):
    _inherit = 'res.partner.member'

    icon = fields.Binary(string='icon')
    # override
    partner_ids = fields.Many2many(
        comodel_name='res.partner',
        domain=[('customer','=',True)],
        copy=False,
        string='Customer')
    
    pricelist_id = fields.Many2one(
        comodel_name='product.pricelist',
        string='Pricelist',domain="[('is_member','=',True)]",
        required=False)

    # override on create & write, karena field many2many tdk ada inverse field
    @api.model
    def create(self, vals):
        res = super(ResPartnerMemberInherit, self).create(vals)
        if res.pricelist_id and res.partner_ids:
            # update pricelist property partner
            res.partner_ids.write({
                'property_product_pricelist': res.pricelist_id.id,
                'active_member_id': res.id,
                })
        return res
    
    @api.multi
    def write(self, values):
        res = super(ResPartnerMemberInherit, self).write(values)
        if values.get('pricelist_id') or values.get('partner_ids'):
            for rec in self:
                rec.partner_ids.write({
                    'property_product_pricelist': rec.pricelist_id.id,
                    'active_member_id': rec.id,
                    })
        return res