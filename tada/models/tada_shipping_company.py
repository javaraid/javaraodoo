from odoo import models, fields, api


class TadaShippingCompany(models.Model):
    _name = "tada.shipping.company"
    _description = "Tada Shipping Company"
    
    shippingCompanyId = fields.Integer('Shipping Company ID')
    brand = fields.Char('Brand Name')
    company_name = fields.Char('Company Name')
    
    