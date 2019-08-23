from datetime import datetime, date
from odoo import fields, models, api, _

class DateReportWizard(models.TransientModel):
    _name = 'date.report.wizard'

    name = fields.Char('Name')
    date_from = fields.Date('Mulai Tanggal')
    date_to = fields.Date('Sampai Tanggal')

    # @api.multi
    # def pdf_bank_customer_report(self):
    #     data = self.read()[0]
    #     datas = {
    #         'ids': [],
    #         'model': 'date.report.wizard',
    #         'form': data
    #     }
    #     return self.env['report'].with_context(landscape=True).get_action(self, 'module_name.template_name', data=datas)    

    @api.multi
    def export(self):
        # data = self.read()[0]
        # objects = {
        #     'ids': [],
        #     'model': 'date.report.wizard',
        #     'form': data
        # }
        return self.env.ref('report_xlsx.partner_xlsx').report_action(self.ids, config=False)

    # def process_wizard(self):
    #     ids_to_change = self._context.get('active_ids')
    #     active_model = self._context.get('active_model')
    #     doc_ids = self.env[active_model].browse(ids_to_change)
    #     doc_ids.confirm_payment()
    #     field_to_write = self.char_fields

        # doc_ids.write(
        #     {
        #         'state' : self.name
        #     }
        # )
