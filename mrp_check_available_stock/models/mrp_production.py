# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    state = fields.Selection(selection_add=[('to_approve','To Approve')])

    def check_available_qty(self):
        if self.availability not in ('assigned','none'):
            if self.bom_id.stock_rule == 'not_less' :
                raise ValidationError(_('Not enough material stock for MO %s or please click CHECK AVAILABILITY button before PRODUCE'%(self.display_name)))
            elif self.bom_id.stock_rule == 'less_approval' and self.state == 'progress' :
                self.state = 'to_approve'
        return self

    @api.multi
    def open_produce_product(self):
        self.check_available_qty()
        return super(MrpProduction, self).open_produce_product()

    @api.multi
    def post_inventory(self):
        to_approve = self.env['mrp.production']
        for rec in self :
            if not self._context.get('force_post'):
                to_approve += rec.check_available_qty()
        return super(MrpProduction, self-to_approve).post_inventory()

    @api.multi
    def action_reject(self):
        for rec in self :
            if rec.state != 'to_approve' :
                continue
            rec.state = 'progress'
