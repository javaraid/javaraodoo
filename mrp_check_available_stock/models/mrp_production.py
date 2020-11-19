# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def check_available_qty(self):
        if self.availability not in ('assigned','none'):
            raise ValidationError(_('Not enough material stock for MO %s or please click CHECK AVAILABILITY button before PRODUCE'%(self.display_name)))

    @api.multi
    def open_produce_product(self):
        self.check_available_qty()
        return super(MrpProduction, self).open_produce_product()
