#vim: set expandtab ts=4 sw=4 filetype=python:

import datetime
import logging
import textwrap

import psycopg2

from budgetbot.webapp.framework.handler import Handler
from budgetbot.webapp.framework.response import Response

from budgetbot.pg import user, expenses

log = logging.getLogger(__name__)

module_template_prefix = 'budgetbotnew'
module_template_package = 'budgetbot.webapp.budgetbotnew.templates'

__all__ = ['TemplateServer']


class TemplateServer(Handler):

    route_strings = dict({
        "GET /":                                 "budgetbotnew/budgetbot.html",
        })

    route = Handler.check_route_strings

    def handle(self, req):

        template_name = self.route_strings[req.line_one]
        return Response.tmpl(template_name, args=req.wz_req.args)

class TemplateRequrieLoginServer(Handler):

    route_strings = dict({
        "GET /analysis":                         "budgetbotnew/analysis.html",
        })

    route = Handler.check_route_strings

    @Handler.require_login
    def handle(self, req):

        template_name = self.route_strings[req.line_one]
        return Response.tmpl(template_name, args=req.wz_req.args)
