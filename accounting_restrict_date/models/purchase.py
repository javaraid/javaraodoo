from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from datetime import datetime, timedelta, date
from calendar import monthrange
from dateutil.relativedelta import relativedelta

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    # date_orders_old = fields.Datetime(string='Order Date', default=datetime.today())

    @api.onchange('date_order')
    def get_date(self):
        user = self.env.user
        if not user.has_group('account.group_account_manager'):
            start_of_month = datetime.today().replace(day=1,hour=0,minute=0,second=0)
            date_order = datetime.strptime(self.date_order, '%Y-%m-%d %H:%M:%S').replace(hour=0,minute=0,second=0)
            if date_order < start_of_month:
                raise UserError('Tidak boleh input dokumen bulan lalu! Hubungi Admin untuk info selengkapnya')

    # @api.multi
    # @api.onchange('date_order')
    # def get_date(self):
    #     for record in self:
    #         user = self.env['res.users'].browse(self.env.uid)
    #         if not user.has_group('account.group_account_manager'):
    #             today = datetime.today()
    #             dates_new = datetime.strptime(str(record.date_order), '%Y-%m-%d %H:%M:%S').strftime('%Y-%m')
    #             dates_new_day = datetime.strptime(str(record.date_order), '%Y-%m-%d %H:%M:%S').strftime('%d')
    #             dates_new_month = datetime.strptime(str(record.date_order), '%Y-%m-%d %H:%M:%S').strftime('%m')
    #             dates_new_year = datetime.strptime(str(record.date_order), '%Y-%m-%d %H:%M:%S').strftime('%Y')
    #             dates_old = datetime.strptime(str(today.date()), '%Y-%m-%d').strftime('%Y-%m')
    #             # dates_old = datetime.strptime(str(record.date_orders_old), '%Y-%m-%d %H:%M:%S').strftime('%Y-%m')
    #             # dates_old_day = datetime.strptime(str(record.date_orders_old), '%Y-%m-%d %H:%M:%S').strftime('%d')
    #             # dates_old_month = datetime.strptime(str(record.date_orders_old), '%Y-%m-%d %H:%M:%S').strftime('%m')
    #             # dates_old_year = datetime.strptime(str(record.date_orders_old), '%Y-%m-%d %H:%M:%S').strftime('%Y')
    #             # dates_old_full = datetime.strptime(str(record.date_orders_old), '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
    #             if dates_new < dates_old:
    #             #     if  dates_old_day < '08':
    #             #         day = monthrange(int(dates_new_year), int(dates_new_month))[1]
    #             #         cal_day = day - 7
    #             #         if dates_new_day < str(cal_day):
    #             #             record.date_order = record.date_orders_old
    #             #             raise UserError('Tidak boleh memilih bulan sebelumnya dari bulan' + dates_old_month + ' dan tahun ' + dates_old_year)
    #             #     else :
    #                     # if dates_new_month < dates_old_month:
    #                 raise UserError('Tidak boleh memilih bulan sebelumnya dari bulan sekarang')
    # @api.multi
    # def write(self,values):
    #     purchase_order_write = super(PurchaseOrder,self).write(values)
    #     if self.date_orders_old != self.date_order:
    #         self.date_orders_old = self.date_order
    #     else:
    #         self.date_orders_old = self.date_orders_old
    #     return purchase_order_write


