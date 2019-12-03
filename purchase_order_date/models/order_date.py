from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from datetime import datetime, timedelta, date
from calendar import monthrange
from dateutil.relativedelta import relativedelta

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    date_orders = fields.Datetime('Order Date', default=datetime.today())
    date_orders_old = fields.Datetime(string='Order Date', default=datetime.today())

    @api.multi
    @api.onchange('date_orders')
    def _get_date(self):
        for record in self:
            if record.date_orders_old != record.date_orders:
                dates_new = datetime.strptime(str(record.date_orders), '%Y-%m-%d %H:%M:%S').strftime('%Y-%m')
                dates_old = datetime.strptime(str(record.date_orders_old), '%Y-%m-%d %H:%M:%S').strftime('%Y-%m')
                dates_old_full = datetime.strptime(str(record.date_orders_old), '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
            
                if dates_new < dates_old:
                    raise UserError('Tidak boleh memilih bulan sebelumnya dari bulan sekarang!')
                    record.date_orders = dates_old_full
                # if dates_new < dates_old and dates_old_days <= '7':
                #     dates_new_month = datetime.date(dates_new_year, dates_new_month, monthrange((dates_new_year), int(dates_new_month))[-1])
                #     dates_new_month_day = mdays[datetime.record.dates_new.month]
                #     dates_old = dates_old_s - timedelta(days=14) 
                #     if dates_new < dates_old:
                #         raise UserError('Tidak boleh memilih bulan sebelumnya dari bulan sekarang!')
                #         record.date_orders = record.date_orders_old
                  



