# vim: set expandtab ts=4 sw=4 filetype=python fileencoding=utf8:

import logging
import re
import textwrap

from budgetbot.webapp.framework.handler import Handler
from budgetbot.webapp.framework.response import Response

__all__ = ['PickupPage', 'SendNewGiftGram','Inbox', 'Sent']

log = logging.getLogger(__name__)

module_template_prefix = 'mockups'
module_template_package = 'budgetbot.webapp.mockups.templates'


class SplashMockup(Handler):

    route_strings = set(['GET /mockup/splash'])

    route = Handler.check_route_strings

    def handle(self, req):

        return Response.tmpl('mockups/splash.html')


