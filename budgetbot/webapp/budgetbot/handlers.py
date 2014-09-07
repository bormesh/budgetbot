#vim: set expandtab ts=4 sw=4 filetype=python:

import logging

from budgetbot.webapp.framework.handler import Handler
from budgetbot.webapp.framework.response import Response

log = logging.getLogger(__name__)

module_template_prefix = 'budgetbot'
module_template_package = 'budgetbot.webapp.budgetbot.templates'

__all__ = ['Splash']

class Splash(Handler):

    route_strings = set(['GET /'])
    route = Handler.check_route_strings

    def handle(self, req):
        return Response.tmpl('budgetbot/splash.html')
