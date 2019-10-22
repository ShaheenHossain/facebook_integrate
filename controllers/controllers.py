# -*- coding: utf-8 -*-
from eagle import http

# class ../atec/facebookAndEagle(http.Controller):
#     @http.route('/../atec/facebook_and_eagle/../atec/facebook_and_eagle/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/../atec/facebook_and_eagle/../atec/facebook_and_eagle/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('../atec/facebook_and_eagle.listing', {
#             'root': '/../atec/facebook_and_eagle/../atec/facebook_and_eagle',
#             'objects': http.request.env['../atec/facebook_and_eagle.../atec/facebook_and_eagle'].search([]),
#         })

#     @http.route('/../atec/facebook_and_eagle/../atec/facebook_and_eagle/objects/<model("../atec/facebook_and_eagle.../atec/facebook_and_eagle"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('../atec/facebook_and_eagle.object', {
#             'object': obj
#         })