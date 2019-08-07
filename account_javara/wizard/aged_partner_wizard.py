from odoo import fields, models, api


class AccountAgedPartnerWizard(models.TransientModel):
    _name = "account.aged.partner.wizard"
    _description = 'Aged Partner Wizard'

    @api.multi
    def generate(self):
        action = self.env.ref('account_reports.action_account_report_ap').read()[0]
        action['context'] = "{'model': 'account.aged.payable.ttf'}"
        return action
