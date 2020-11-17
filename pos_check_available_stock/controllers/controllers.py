# -*- coding: utf-8 -*-
from odoo import http

# class PosCheckAvailableStock(http.Controller):
#     @http.route('/pos_check_available_stock/pos_check_available_stock/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_check_available_stock/pos_check_available_stock/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_check_available_stock.listing', {
#             'root': '/pos_check_available_stock/pos_check_available_stock',
#             'objects': http.request.env['pos_check_available_stock.pos_check_available_stock'].search([]),
#         })

#     @http.route('/pos_check_available_stock/pos_check_available_stock/objects/<model("pos_check_available_stock.pos_check_available_stock"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_check_available_stock.object', {
#             'object': obj
#         })