# -*- coding: utf-8 -*-
from odoo import http

# class CheckAvailableStock(http.Controller):
#     @http.route('/check_available_stock/check_available_stock/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/check_available_stock/check_available_stock/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('check_available_stock.listing', {
#             'root': '/check_available_stock/check_available_stock',
#             'objects': http.request.env['check_available_stock.check_available_stock'].search([]),
#         })

#     @http.route('/check_available_stock/check_available_stock/objects/<model("check_available_stock.check_available_stock"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('check_available_stock.object', {
#             'object': obj
#         })