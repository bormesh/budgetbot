# vim: set expandtab ts=4 sw=4 filetype=python:

import logging
import textwrap

import decorator

from horsemeat.webapp import handler

from budgetbot.webapp.framework.response import Response

log = logging.getLogger(__name__)

module_template_prefix = 'framework'
module_template_package = 'budgetbot.webapp.framework.templates'

class Handler(handler.Handler):

    @property
    def four_zero_four_template(self):
        return 'framework_templates/404.html'

    def not_found(self, req):

        return super(Handler, self).not_found(req)

    @staticmethod
    @decorator.decorator
    def require_login(handler_method, self, req):

        """
        Add this to a handle method like this::

            @Handler.require_login
            def handle(self, req):
                ...

        And then, if the request isn't from a signed-in user,
        they'll get the JSON reply below.

        If the request is from a signed-in user, then your handle
        method is normal.
        """

        if not req.user:

            return Response.json(dict(
                reply_timestamp=datetime.datetime.now(),
                message="Sorry, you need to log in first!",
                needs_to_log_in=True,
                success=False))

        else:
            return handler_method(self, req)


    required_json_keys = []

    def check_all_required_keys_in_json(self, req):
        return all(k in req.json for k in self.required_json_keys)

    def find_missing_json_keys(self, req):
        return [k for k in self.required_json_keys if k not in req.json]


    @staticmethod
    @decorator.decorator
    def require_json(handler_method, self, req):

        """
        Add this to a handle method like this::

            required_json_keys = ['A', 'B']

            @Handler.require_json
            def handle(self, req):
                ...

        And then, if the request isn't a JSON request with keys A and B,
        they'll get the JSON reply below.

        """

        if not req.is_JSON \
        or not req.json:

            return Response.json(dict(
                reply_timestamp=datetime.datetime.now(),
                message="Sorry, must be a JSON request!",
                success=False))

        elif not self.check_all_required_keys_in_json(req):

            missing_json_keys = self.find_missing_json_keys(req)

            log.error("Request {0} didn't have these keys: {1}".format(
                req.line_one,
                missing_json_keys))

            return Response.json(dict(
                success=False,
                reply_timestamp=datetime.datetime.now(),
                message="Sorry, you are missing keys: [{0}]!".format(
                    ", ".join(self.find_missing_json_keys(req)))))

        else:
            return handler_method(self, req)

    required_user_groups = []

    def check_user_group_in_required_groups(self, req):
        return req.user.group_title in self.required_user_groups


