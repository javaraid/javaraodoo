from odoo import api, fields, models,_
from odoo.exceptions import ValidationError

class ResPartnerMember(models.Model):
    _inherit = 'res.partner.member'

    # override
    icon = fields.Binary(string='icon')

    partner_ids = fields.One2many(
        comodel_name='res.partner.member.detail',
        inverse_name='partner_member_id',
        copy=False,
        string='Customer',)
    
    pricelist_id = fields.Many2one(
        comodel_name='product.pricelist',
        string='Pricelist',domain="[('is_member','=',True)]",
        required=False)
 

    

    # override
    @api.constrains('partner_ids')
    def _check_partner(self):
        # TODO: validasi bahwa hanya 1 partner di 1 member
         for rec in self :
            if rec.partner_ids :
                other_members = self.search([
                    ('partner_ids','=',rec.partner_ids.ids),
                    ('id','!=',rec.id),
                ])
                if other_members :
                    raise ValidationError(_('Some customers was added in other member.'))
    
class ResPartnerMemberDetail(models.Model):
    _name = 'res.partner.member.detail'
    _description = 'Detail partner member'

    partner_member_id = fields.Many2one(comodel_name='res.partner.member', 
        string='Partner Member')
    partner_id = fields.Many2one(comodel_name='res.partner', string='Customer',
        domain="[('customer','=',True)]")

    # active / state