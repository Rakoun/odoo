# -*- coding: utf-8 -*-
from odoo import http

# class MyLibraryReturn(http.Controller):
#     @http.route('/my_library_return/my_library_return/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/my_library_return/my_library_return/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('my_library_return.listing', {
#             'root': '/my_library_return/my_library_return',
#             'objects': http.request.env['my_library_return.my_library_return'].search([]),
#         })

#     @http.route('/my_library_return/my_library_return/objects/<model("my_library_return.my_library_return"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('my_library_return.object', {
#             'object': obj
#         })