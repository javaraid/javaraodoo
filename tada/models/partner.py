from odoo import models, fields, api

CustomerUrl = '/v1/integration_merchants/customers/{id}'


class Partner(models.Model):
    _inherit = 'res.partner'
    
    tadaid = fields.Integer('ID on Tada')
    sex = fields.Char()
    birthday = fields.Date()
    
    @api.model
    def _get_from_tada(self, access_token, tadaid):
        Tags = ['res.partner.category']
        base_api_url = self.env['ir.config_parameter'].sudo().get_param('tada.base_api_url')
        authorization = 'Bearer {}'.format(access_token)
        headers = {'Content-Type': 'application/json', 'Authorization': authorization}
        auth_response = requests.get(base_api_url + CustomerUrl, headers=headers, timeout=10.0)
        resp_json = auth_response.json()
        tadaid = resp_json['id'] # id
        name = resp_json['name'] # name
        email = resp_json['email'] # email
        phone = resp_json['phone'] # phone
        sex = resp_json['sex'] # sex
        birthday = resp_json['birthday'] # birthday
        createdAt = resp_json['createdAt'] # createdAt
        active = resp_json['active'] # active
        zip = resp_json['additionalData']['postal_code'] # additionalData.postal_code
        vals = {'tadaid': tadaid,
                'name': name,
                'email': email,
                'phone': phone,
                'sex': sex,
                'birthday': birthday,
                'createdAt': createdAt,
                'active': active,
                'zip': zip}
#         Tags.search([('tadaid')])
        return
    
    @api.model
    def _upsert_customer_tada(self, resp_dict, partners_tadaid, partners_phone):
        tadaid = resp_dict['id']
        name = resp_dict['firstName']
        email = resp_dict['email']
        phone = resp_dict['phone']
        street = resp_dict['address']
        zip = resp_dict['postalCode']
        vals = {'tadaid': tadaid,
                'name': name,
                'email': email,
                'phone': phone,
                'street': street,
                'zip': zip,
                'customer': True}
        partner_found = partners_tadaid.get(tadaid, False)
        if not partner_found:
            partners_found = partners_phone.get(phone, False)
        if partner_found:
            partner_id = self.browse(partner_found)
            partner_id.write(vals)
        else:
            vals.update({'active': False})
            partner_id = self.create(vals)
            partners_tadaid.update({tadaid: partner_id.id})
            partners_phone.update({phone: partner_id.id})
        return partner_id.id
        
class PartnerCategory(models.Model):
    _inherit = 'res.partner.category'
    
    tadaid = fields.Integer()
    
    