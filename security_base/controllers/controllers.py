# -*- coding: utf-8 -*-
from odoo import http

# class SecurityBase(http.Controller):
#     @http.route('/security_base/security_base/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/security_base/security_base/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('security_base.listing', {
#             'root': '/security_base/security_base',
#             'objects': http.request.env['security_base.security_base'].search([]),
#         })

#     @http.route('/security_base/security_base/objects/<model("security_base.security_base"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('security_base.object', {
#             'object': obj
#         })