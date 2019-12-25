from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from datetime import datetime, timedelta, date
from calendar import monthrange
from dateutil.relativedelta import relativedelta

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    date_orders_old = fields.Datetime(string='Order Date', default=datetime.today())
    # purchase_ids = fields.One2many(comodel_name='purchase.order.line', inverse_name='purchase_id', string='Purchase Ids')
    qty_rec = fields.Float(string='Qty Received', store=True, compute='_get_qty_rec')

    @api.multi
    @api.depends('order_line.qty_received')
    def _get_qty_rec(self):
        for rec in self:
            total = 0.0
            for line in self.order_line:
                total += line.qty_received
            rec.qty_rec = total

    @api.multi
    @api.onchange('date_order')
    def _get_date(self):
        for record in self:
            user = self.env['res.users'].browse(self.env.uid)
            if not user.has_group('account.group_account_manager'):
                dates_new = datetime.strptime(str(record.date_order), '%Y-%m-%d %H:%M:%S').strftime('%Y-%m')
                dates_new_day = datetime.strptime(str(record.date_order), '%Y-%m-%d %H:%M:%S').strftime('%d')
                dates_new_month = datetime.strptime(str(record.date_order), '%Y-%m-%d %H:%M:%S').strftime('%m')
                dates_new_year = datetime.strptime(str(record.date_order), '%Y-%m-%d %H:%M:%S').strftime('%Y')
                dates_old = datetime.strptime(str(record.date_orders_old), '%Y-%m-%d %H:%M:%S').strftime('%Y-%m')
                dates_old_day = datetime.strptime(str(record.date_orders_old), '%Y-%m-%d %H:%M:%S').strftime('%d')
                dates_old_month = datetime.strptime(str(record.date_orders_old), '%Y-%m-%d %H:%M:%S').strftime('%m')
                dates_old_year = datetime.strptime(str(record.date_orders_old), '%Y-%m-%d %H:%M:%S').strftime('%Y')
                dates_old_full = datetime.strptime(str(record.date_orders_old), '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
                if dates_new < dates_old:
                    if  dates_old_day < '08':
                        day = monthrange(int(dates_new_year), int(dates_new_month))[1]
                        cal_day = day - 7
                        if dates_new_day < str(cal_day):
                            record.date_order = record.date_orders_old
                            raise UserError('Tidak boleh memilih bulan sebelumnya dari bulan' + dates_old_month + ' dan tahun ' + dates_old_year)
                    else :
                        if dates_new_month < dates_old_month:
                            record.date_order = record.date_orders_old
                            raise UserError('Tidak boleh memilih bulan sebelumnya dari bulan' + dates_old_month + ' dan tahun ' + dates_old_year)
    @api.multi
    def write(self,values):
        purchase_order_write = super(PurchaseOrder,self).write(values)
        if self.date_orders_old != self.date_order:
            self.date_orders_old = self.date_order
            return purchase_order_write

# class PurchaseOrderLine(models.Model):
#     _inherit = 'purchase.order.line'

#     purchase_id = fields.Many2one(comodel_name='purchase.order', string='Purchase Id')
#     purchase_idds = fields.One2many(comodel_name='purchase.report', inverse_name='purchase_idd', string='Purchase Idds')
#     qty_recs = fields.Float(related='purchase_id.qty_rec', string='Quantity Received', store=True)
    
   

# class PurchaseReport(models.Model):
#     _inherit = "purchase.report"

#     purchase_idd = fields.Many2one(comodel_name='purchase.order.line', string='Purchase Idd')
#     qty_recss = fields.Float(related='purchase_idd.qty_recs', string='Quantity Received', store=True)
#     qty_receiveds = fields.Float('Qty Received')

#     def _select(self):
#         return super(PurchaseReport, self)._select() + ", qty_recss as qty_receiveds"
    

