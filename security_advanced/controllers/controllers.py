# -*- coding: utf-8 -*-
from odoo import http

# class SecurityAdvanced(http.Controller):
#     @http.route('/security_advanced/security_advanced/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/security_advanced/security_advanced/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('security_advanced.listing', {
#             'root': '/security_advanced/security_advanced',
#             'objects': http.request.env['security_advanced.security_advanced'].search([]),
#         })

#     @http.route('/security_advanced/security_advanced/objects/<model("security_advanced.security_advanced"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('security_advanced.object', {
#             'object': obj
#         })