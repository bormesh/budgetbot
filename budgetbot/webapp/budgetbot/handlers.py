#vim: set expandtab ts=4 sw=4 filetype=python:

import datetime
import logging
import textwrap

import psycopg2

from budgetbot.webapp.framework.handler import Handler
from budgetbot.webapp.framework.response import Response

from budgetbot.pg import user, expenses

log = logging.getLogger(__name__)

module_template_prefix = 'budgetbot'
module_template_package = 'budgetbot.webapp.budgetbot.templates'

__all__ = ['TemplateServer', 'Splash', 'ShoppingListTemplate', 'InsertExpense', 'UserSearch']


class TemplateServer(Handler):

    route_strings = dict({
        "GET /bb":                              "budgetbot/budgetbot.html",
        "GET /old":                                 "budgetbot/budgetbot.html",
        # "GET /weekly-manifests":              "budgetbot/weeklymanifests.html",
        "GET /login":                           "budgetbot/login.html",
        "GET /expenses":                        "budgetbot/splash.html",
        "GET /reset-password":                  "budgetbot/reset-password.html",
        })

    route = Handler.check_route_strings

    def handle(self, req):

        template_name = self.route_strings[req.line_one]
        return Response.tmpl(template_name, args=req.wz_req.args)


class ExpensesPeopleAndCategories(Handler):

    route_strings = set(['GET /api/expense-categories'])
    route = Handler.check_route_strings

    @Handler.require_login
    def handle(self, req):

        people = user.Person.get_all(self.cw.get_pgconn())

        expense_categories_denormal = expenses.\
            ExpenseCategoriesDenormalized. \
            get_all_with_budgets(self.cw.get_pgconn())

        expense_categories = expenses.\
            ExpenseCategories.get_all(self.cw.get_pgconn())

        if(req.user and (req.user.email_address == 'rob@216software.com' or
            req.user.email_address == 'Debby.heinen@gmail.com')):

           return Response.json(dict(
                reply_timestamp=datetime.datetime.now(),
                success=True,
                expense_categories_denormal\
                =expense_categories_denormal,
                expense_categories=expense_categories,
                message="People and categories"))




class ShoppingListTemplate(Handler):

    route_strings = set(['GET /shopping-list'])
    route = Handler.check_route_strings

    def handle(self, req):

        return Response.tmpl('budgetbot/shopping-list.html')



class InsertExpense(Handler):

    route_strings = set(['POST /api/insert-expense'])
    route = Handler.check_route_strings

    def handle(self, req):

        if not req.json:
            return Response.json({'success':'false'})

        log.debug(req.json)

        expense_uuid = self.insert_expense(req.user.person_uuid,
                            req.json['amount'],
                            req.json['expense_date'],
                            req.json['expense_category'],
                            req.json.get('extra_notes'))

        return Response.json({'success':'true',
                              'data':{'expense_uuid':expense_uuid}})

    def insert_expense(self, person_uuid, amount, expense_date,
                       expense_category, extra_notes=None):

        pgconn = self.cw.get_pgconn()

        cursor = pgconn.cursor()

        cursor.execute("""

            insert into expenses

            (person_uuid, amount, expense_date, expense_category,
             extra_notes)

            values

            ( %(person_uuid)s, %(amount)s,
              %(expense_date)s, %(expense_category)s,
              %(extra_notes)s)

            returning expense_uuid

        """, {'person_uuid':person_uuid, 'amount':amount,
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


class UserSearch(Handler):

    route_strings = set(['GET /api/user-search'])
    route = Handler.check_route_strings

    @Handler.require_login
    def handle(self, req):

        log.info("searching for {0}".format(req.wz_req.args.get('search_query')))

        cursor = self.cw.get_pgconn().cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Search with both trigrams using similarity and tsquery

        cursor.execute(textwrap.dedent("""
            select p1.email_address, p1.display_name, p1.person_uuid,
            similarity(p1.email_address, %(search_query)s) as email_sim,
            similarity(p1.display_name, %(search_query)s) as disp_sim,
            p1.search_field

            from (
                select email_address, display_name, person_uuid,
                to_tsvector('simple', email_address) ||
                to_tsvector('simple', display_name) as search_field
                from people
            ) p1

            where p1.search_field @@ plainto_tsquery(%(search_query)s)
            or
            (similarity(p1.email_address, %(search_query)s) +
            similarity(p1.display_name, %(search_query)s)) > .6

        """),{'search_query':req.wz_req.args['search_query']})

        if cursor.rowcount:
            results = cursor.fetchall()
        else:
            results = list()

        return Response.json(dict(
            reply_timestamp=datetime.datetime.now(),
            success=True,
            search_results=results,
            num_results = len(results),
            message="Search results returned"))



