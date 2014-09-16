#vim: set expandtab ts=4 sw=4 filetype=python:

import logging

from budgetbot.webapp.framework.handler import Handler
from budgetbot.webapp.framework.response import Response

from budgetbot.pg import user, expenses

log = logging.getLogger(__name__)

module_template_prefix = 'budgetbot'
module_template_package = 'budgetbot.webapp.budgetbot.templates'

__all__ = ['Splash']

class Splash(Handler):

    route_strings = set(['GET /'])
    route = Handler.check_route_strings

    def handle(self, req):
        people = user.Person.get_all(self.cw.get_pgconn())

        expense_categories = expenses.ExpenseCategories. \
            get_all(self.cw.get_pgconn())

        log.debug('{0}'.format(expense_categories))
        return Response.tmpl('budgetbot/splash.html',
                             people=people,
                             expense_categories=expense_categories)

class ExpenseInputPage(Handler):

    route_strings = set(['GET /enter-expense'])
    route = Handler.check_route_strings

    def handle(self, req):

        people = user.Person.get_all(self.cw.get_pgconn())

        expense_categories = ['one', 'two', 'three']

        return Response.tmpl('budgetbot/new-expense-form.html',
                             people=people,
                             expense_categories=expense_categories)

