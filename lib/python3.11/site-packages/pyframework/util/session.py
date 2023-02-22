# # -*- coding: utf-8 -*-
#
# from pyframework.util.string.serialization.json import JsonHelper
#
#
# class SessionHelper:
#     def key(self, identifier):
#         return 'session_%s' % (identifier.replace('-', '_'))
#
#     def is_authorized(self, controller, identifier):
#         return True if self.authorized(controller=controller, identifier=identifier) else False
#
#     def authorize(self, controller, identifier, payload, after=None, before=None):
#         if not isinstance(payload, dict):
#             return False
#
#         if before and before(payload) is False:
#             return False
#
#         controller.session(
#             name=self.key(identifier),
#             value=JsonHelper.stringify(payload),
#             expire_in=self.ini.session.expire_in)
#
#         if after and self.is_authorized(identifier=identifier, controller=controller):
#             after(payload)
#
#         return True
#
#     def unauthorize(self, controller, identifier):
#         controller.session(self.key(identifier), '', expire_in=0)
#         return True
#
#     def authorized(self, controller, identifier):
#         controller = controller if isinstance(controller, dpHandler) else controller.parent
#
#         # Return temporary session if exist
#         if hasattr(controller, self.key(identifier)):
#             return getattr(controller, self.key(identifier))
#
#         payload = controller.session(name=self.key(identifier), expire_in=self.ini.session.expire_in)
#
#         if not payload:
#             return False
#
#         payload = self.helper.serialization.json.parse(payload)
#
#         # Save temporary session for current session
#         if payload:
#             setattr(controller, self.key(identifier), payload)
#
#         return payload
