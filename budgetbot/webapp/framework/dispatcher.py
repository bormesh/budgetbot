# vim: set expandtab ts=4 sw=4 filetype=python fileencoding=utf-8:
# -*- coding: utf-8 -*-

import logging

from horsemeat.webapp import dispatcher

from budgetbot.webapp.framework import request

log = logging.getLogger(__name__)

class Dispatcher(dispatcher.Dispatcher):

    request_class = request.Request

    def make_handlers(self):

        log.info('Making budgetbot handlers...')

        self.handlers.extend(self.make_handlers_from_module_string(
            'budgetbot.webapp.mockups.handlers'))

        #self.handlers.extend(self.make_handlers_from_module_string(
        #    'budgetbot.webapp.auth.handlers'))
        self.handlers.extend(self.make_handlers_from_module_string(
            'budgetbot.webapp.ajaxauth.handlers'))

        self.handlers.extend(self.make_handlers_from_module_string(
            'budgetbot.webapp.dashboard.handlers'))

        self.handlers.extend(self.make_handlers_from_module_string(
            'budgetbot.webapp.budgetbot.handlers'))

        self.handlers.extend(self.make_handlers_from_module_string(
            'budgetbot.webapp.budgetbotnew.handlers'))

        self.handlers.extend(self.make_handlers_from_module_string(
            'budgetbot.webapp.shoppinglist.handlers'))

        self.handlers.extend(self.make_handlers_from_module_string(
            'budgetbot.webapp.timetracking.handlers'))

        self.handlers.extend(self.make_handlers_from_module_string(
            'budgetbot.webapp.notfound.handlers'))

    @property
    def error_page(self):

        log.debug("Getting error template...")

        j = self.cw.get_jinja2_environment()

        t = j.get_template('budgetbot/error.html')

        return t

