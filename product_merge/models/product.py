# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import datetime, timedelta
import logging
import pytz

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def merge_product(self):
        total = len(self.search([('create_uid', '=', 17)]))
        loop = 0
        for prod_to_del in self.search([('create_uid', '=', 17)]):
            # find original variant from its template
            tmpl = prod_to_del.product_tmpl_id
            prod_to_merge = [
                prod for prod in tmpl.product_variant_ids if prod.id != prod_to_del.id]
            if not prod_to_merge:
                _logger.error('\n==== PRODUCT NAME: %S ====' % prod_to_del.name)
            # set not available in pos
            self.env.cr.execute(
                'UPDATE product_template SET available_in_pos=null where id=%i' % prod_to_del.product_tmpl_id.id)
            # merge product in pos order line
            self.env.cr.execute(
                'UPDATE pos_order_line SET product_id=%i where id=%i' % (prod_to_merge[0].id, prod_to_del.id,))
            loop += 1
            progress = loop / total * 100
            _logger.error('\n==== MERGE POS ORDER LINE PROGRESS: %i %% ====' % int(progress))
