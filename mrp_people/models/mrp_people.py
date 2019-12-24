# from odoo import models, fields, api, _
# from odoo.tools.float_utils import float_compare, float_round, float_is_zero
# from odoo.exceptions import UserError
from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from odoo.tools import float_compare
from datetime import datetime

class MrpPeople(models.Model):
    _name = 'mrp.people'

    name = fields.Char('Worker Name')
    # name_id = fields.Many2one(_name, 'Worker Name')
    # people_id = fields.Many2one('mrp.production')
    order_ids = fields.Many2many('mrp.production', string='Orders')


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    # people_ids = fields.One2many('mrp.people', 'people_id' ,'Worker Name')
    people_ids = fields.Many2many('mrp.people', string='Workers')
    people_count = fields.Integer(compute='_get_people_count', store=True, string='Worker')
    done_at =  fields.Datetime(string='Done At')
    days = fields.Integer(compute='_get_date', store=True, string='Days')

    @api.multi
    @api.depends('people_ids.name') 
    def _get_people_count(self): 
        for record in self:   
            record.people_count = len(record.people_ids)

    @api.multi
    def button_mark_done(self):
        for record in self:
            if not record.people_ids:
                raise UserError('Worker harus diisi!')
            record.done_at = datetime.now()
            record.write({'state': 'done'})

    @api.multi
    @api.depends('done_at')
    def _get_date(self):
        for record in self:
            if not record.done_at:
                record.done_at = False
            else:
                from_date = datetime.strptime(str(record.date_planned_start), '%Y-%m-%d %H:%M:%S')
                to_date = datetime.strptime(str(record.done_at), '%Y-%m-%d %H:%M:%S')
                timedelta = to_date - from_date
                diff_day = timedelta.days
                record.days = diff_day
            

    
    


    
