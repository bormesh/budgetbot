#vim: set expandtab ts=4 sw=4 filetype=python:

import logging
import textwrap

from budgetbot.webapp.framework.handler import Handler
from budgetbot.webapp.framework.response import Response

from budgetbot.pg import user, expenses

log = logging.getLogger(__name__)

module_template_prefix = 'budgetbot'
module_template_package = 'budgetbot.webapp.budgetbot.templates'

__all__ = ['TemplateServer', 'Splash', 'ShoppingListTemplate', 'InsertExpense']


class TemplateServer(Handler):

    route_strings = dict({
        "GET /bb":                              "budgetbot/budgetbot.html",
        # "GET /weekly-manifests":              "budgetbot/weeklymanifests.html",
        "GET /login":                           "budgetbot/login.html",
        "GET /reset-password":                  "budgetbot/reset-password.html",
        })

    route = Handler.check_route_strings

    def handle(self, req):

        template_name = self.route_strings[req.line_one]
        return Response.tmpl(template_name, args=req.wz_req.args)


class Splash(Handler):

    route_strings = set(['GET /'])
    route = Handler.check_route_strings

    def handle(self, req):
        people = user.Person.get_all(self.cw.get_pgconn())

        expense_categories_denormal = expenses.\
            ExpenseCategoriesDenormalized. \
            get_all_with_budgets(self.cw.get_pgconn())

        return Response.tmpl('budgetbot/splash.html',
                             people=people,
                             expense_categories_denormal\
                             =expense_categories_denormal)

class ShoppingListTemplate(Handler):

    route_strings = set(['GET /shopping-list'])
    route = Handler.check_route_strings

    def handle(self, req):

        return Response.tmpl('budgetbot/shopping-list.html')



class InsertExpense(Handler):

    route_strings = set(['POST /insert-expense'])
    route = Handler.check_route_strings

    def handle(self, req):

        log.info("adding expense new")

        if not req.json:
            return Response.json({'success':'false'})

        log.info("req json is {0}".format(req.json))

        expense_uuid = self.insert_expense(req.json['person_id'],
                            req.json['amount'],
                            req.json['expense_date'],
                            req.json['expense_category'],
                            req.json.get('extra_notes'))

        return Response.json({'success':'true',
                              'data':{'expense_uuid':expense_uuid}})

    def insert_expense(self, person_id, amount, expense_date,
                       expense_category, extra_notes=None):

        pgconn = self.cw.get_pgconn()

        cursor = pgconn.cursor()

        cursor.execute("""

            insert into expenses

            (person_id, amount, expense_date, expense_category,
             extra_notes)

            values

            ( %(person_id)s, %(amount)s,
              %(expense_date)s, %(expense_category)s,
              %(extra_notes)s)

            returning expense_uuid

        """, {'person_id':person_id, 'amount':amount,
               'expense_date':expense_date,
               'expense_category':expense_category,
               'extra_notes':extra_notes})


        return cursor.fetchone().expense_uuid


class DeleteExpense(Handler):

    route_strings = set(['POST /delete-expense'])
    route = Handler.check_route_strings

    def handle(self, req):

        log.info("adding expense new")

        if not req.json:
            return Response.json({'success':'false'})

        log.info("req json is {0}".format(req.json))

        cursor = self.cw.get_pgconn().cursor()

        cursor.execute(textwrap.dedent("""

            delete from expenses

            where expense_uuid = %(expense_uuid)s

        """),{'expense_uuid':req.json['expense_uuid']})

        return Response.json({'success':'true'})



