from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from datetime import datetime, timedelta, date
from calendar import monthrange
from dateutil.relativedelta import relativedelta

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    # date_orders_old = fields.Date(string='Order Date', default=datetime.today())

    @api.onchange('date_invoice')
    def get_date(self):
        user = self.env.user
        if not user.has_group('account.group_account_manager'):
            start_of_month = datetime.today().replace(day=1,hour=0,minute=0,second=0)
            date_invoice = datetime.strptime(self.date_invoice, '%Y-%m-%d %H:%M:%S').replace(hour=0,minute=0,second=0)
            if date_invoice < start_of_month:
                raise UserError('Tidak boleh input dokumen bulan lalu! Hubungi Admin untuk info selengkapnya')

    # @api.onchange('date_invoice')
    # def _get_date(self):
    #     for record in self:
    #         user = self.env['res.users'].browse(self.env.uid)
    #         if not user.has_group('account.group_account_manager'):
    #             if record.date_invoice != False:
    #                 # record.date_invoice = datetime.today()
    #                 today = datetime.today()
    #                 dates_new = datetime.strptime(str(record.date_invoice), '%Y-%d-%m').strftime('%Y-%m')
    #                 dates_new_day = datetime.strptime(str(record.date_invoice), '%Y-%d-%m').strftime('%d')
    #                 dates_new_month = datetime.strptime(str(record.date_invoice), '%Y-%d-%m').strftime('%m')
    #                 dates_new_year = datetime.strptime(str(record.date_invoice), '%Y-%d-%m').strftime('%Y')
    #                 dates_old = datetime.strptime(str(today.date()), '%Y-%m-%d').strftime('%Y-%m')
    #                 # dates_old = datetime.strptime(str(record.date_orders_old), '%Y-%m-%d').strftime('%Y-%m')
    #                 # dates_old_day = datetime.strptime(str(record.date_orders_old), '%Y-%m-%d').strftime('%d')
    #                 # dates_old_month = datetime.strptime(str(record.date_orders_old), '%Y-%m-%d').strftime('%m')
    #                 # dates_old_year = datetime.strptime(str(record.date_orders_old), '%Y-%m-%d').strftime('%Y')
    #                 # dates_old_full = datetime.strptime(str(record.date_orders_old), '%Y-%m-%d').strftime('%Y-%m-%d')
    #                 if dates_new < dates_old:
    #                 #     if  dates_old_day < '08':
    #                 #         day = monthrange(int(dates_new_year), int(dates_new_month))[1]
    #                 #         cal_day = day - 7
    #                 #         if dates_new_day < str(cal_day):
    #                 #             record.date_order = record.date_orders_old
    #                 #             raise UserError('Tidak boleh memilih bulan sebelumnya dari bulan' + dates_old_month + ' dan tahun ' + dates_old_year)
    #                 #     else :
    #                 # if dates_new_month < dates_old_month:
    #                     # record.date_invoice = record.date_orders_old
    #                     raise UserError('Tidak boleh memilih bulan sebelumnya dari bulan sekarang')
    # @api.multi
    # def write(self,values):
    #     account_invoice_write = super(AccountInvoice,self).write(values)
    #     if self.date_orders_old != self.date_invoice:
    #         self.date_orders_old = self.date_invoice
    #     else:
    #         self.date_orders_old = self.date_orders_old
    #     return account_invoice_write


