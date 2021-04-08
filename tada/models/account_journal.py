from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountJournal(models.Model):
    _inherit = 'account.journal'
    
    is_tada_available = fields.Boolean('Available on Tada')
    
    @api.constrains('is_tada_available')
    def _check_available_tada(self):
        if self.is_tada_available == False:
            return
        available_exist = self.search([('is_tada_available', '=', True), ('id', '!=', self.id), ('company_id', '=', self.company_id.id)], limit=1)
        if available_exist.id:
            raise UserError(_('There must be only one journal only available. Please set inactive other.'))
    