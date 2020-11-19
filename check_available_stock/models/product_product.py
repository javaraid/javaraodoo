# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductProduct(models.Model):
    _inherit = 'product.product'

    def get_available_qty_by_location(self, location_id):
        self.ensure_one()
        available_qty = self.env['stock.quant']._get_available_quantity(product_id=self, location_id=location_id)
        print("\n available_qty",available_qty)
        return available_qty
