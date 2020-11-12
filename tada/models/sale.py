from odoo import models, fields, api


class CrmTeam(models.Model):
    _inherit = 'crm.team'
    
    team_type = fields.Selection(selection_add=[('tada', 'Tada')])
    

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    
    
    