# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import datetime, timedelta
import logging
import pytz

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class StockQuant(models.Model):
    _inherit = 'stock.quant'
# PM: label CCO Jerrycan
# RM: Cempo Hitam Unpolished | Pecah Kulit

    def merge_quant(self, product_id=False, location_id=False):
        Product = self.env['product.product']
        Location = self.env['stock.location']
        MoveLine = self.env['stock.move.line']
        product_ids = [product_id] if product_id else \
            Product.search([]).ids
        location_ids = [location_id] if location_id else \
            Location.search([]).ids
        # count total
        total = 0
        for product_id in product_ids:
            for location_id in location_ids:
                quants = self.search([('product_id', '=', product_id),
                                      ('location_id', '=', location_id)])
                if len(quants) > 1:
                    total += 1
        # start
        loop = 0
        for product_id in product_ids:
            for location_id in location_ids:
                quants = self.search([('product_id', '=', product_id),
                                      ('location_id', '=', location_id)])
                if len(quants) > 1:
                    quant = quants[0]
                    quants_to_del = \
                        [quants[i] for i in range(1, len(quants) - 1)]
                    for quant_to_del in quants_to_del:
                        quant_to_del.unlink()
                    domain = [
                        ('product_id', '=', product_id),
                        ('lot_id', '=', quant.lot_id.id),
                        '|',
                        ('package_id', '=', quant.package_id.id),
                        ('result_package_id', '=', quant.package_id.id),
                    ]
                    lines_from_loc = MoveLine.search(
                        domain + [('location_id', '=', location_id)])
                    lines_to_loc = MoveLine.search(
                        domain + [('location_dest_id', '=', location_id)])
                    # write quantity
                    qty_from = sum([line.qty_done for line in lines_from_loc])
                    qty_to = sum([line.qty_done for line in lines_to_loc])
                    qty = qty_to - qty_from
                    # write reserved
                    qty_reserved_from = sum(
                        [line.product_uom_qty for line in lines_from_loc])
                    qty_reserved_to = sum(
                        [line.product_uom_qty for line in lines_to_loc])
                    qty_reserved = qty_reserved_to - qty_reserved_from
                    quant.write({
                        'quantity': qty,
                        'reserved_quantity': qty_reserved,
                    })
                    loop += 1
                    _logger.info(
                        '== MERGE PROGRESS: %i%% ==' % int(loop / total * 100))
                    if loop == total:
                        break

        # total = len(self.search([('create_uid', '=', 17)]))
        # loop = 0
        # for prod_to_del in self.search([('create_uid', '=', 17)]):
        #     # find original variant from its template
        #     tmpl = prod_to_del.product_tmpl_id
        #     prod_to_merge = [
        #         prod for prod in tmpl.product_variant_ids if prod.id != prod_to_del.id]
        #     if not prod_to_merge:
        #         # set not available in pos
        #         self.env.cr.execute(
        #             'UPDATE product_template SET available_in_pos=null where id=%i' % prod_to_del.product_tmpl_id.id)
        #         loop += 1
        #         _logger.error(
        #             '== MERGE PROGRESS: %i%% ==' % int(loop / total * 100))
        #         continue
        #     # set not available in pos
        #     self.env.cr.execute(
        #         'UPDATE product_template SET available_in_pos=null where id=%i' % prod_to_del.product_tmpl_id.id)
        #     # merge product in pos order line
        #     self.env.cr.execute(
        #         'UPDATE pos_order_line SET product_id=%i where product_id=%i' % (prod_to_merge[0].id, prod_to_del.id,))
        #     # merge product in stock move
        #     self.env.cr.execute(
        #         'UPDATE stock_move SET product_id=%i where product_id=%i' % (prod_to_merge[0].id, prod_to_del.id,))
        #     # merge product in stock inventory line
        #     self.env.cr.execute(
        #         'UPDATE stock_inventory_line SET product_id=%i where product_id=%i' % (prod_to_merge[0].id, prod_to_del.id,))
        #     # merge product in stock quant
        #     self.env.cr.execute(
        #         'UPDATE stock_quant SET product_id=%i where product_id=%i' % (prod_to_merge[0].id, prod_to_del.id,))
        #     # merge product in MO
        #     self.env.cr.execute(
        #         'UPDATE mrp_production SET product_id=%i where product_id=%i' % (prod_to_merge[0].id, prod_to_del.id,))
        #     # merge product in BoM
        #     self.env.cr.execute(
        #         'UPDATE mrp_bom_line SET product_id=%i where product_id=%i' % (prod_to_merge[0].id, prod_to_del.id,))
        #     # merge product in invoice
        #     self.env.cr.execute(
        #         'UPDATE account_invoice_line SET product_id=%i where product_id=%i' % (prod_to_merge[0].id, prod_to_del.id,))
        #     # merge product in sale
        #     self.env.cr.execute(
        #         'UPDATE sale_order_line SET product_id=%i where product_id=%i' % (prod_to_merge[0].id, prod_to_del.id,))
        #     # merge product in purchase
        #     self.env.cr.execute(
        #         'UPDATE purchase_order_line SET product_id=%i where product_id=%i' % (prod_to_merge[0].id, prod_to_del.id,))
        #     loop += 1
        #     _logger.error(
        #         '== MERGE PROGRESS: %i%% ==' % int(loop / total * 100))
