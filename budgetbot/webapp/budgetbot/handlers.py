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

        log.info(req.user.email_address)

        if(req.user and (req.user.email_address == 'rob@216software.com' or
            req.user.email_address == 'debby.heinen@gmail.com')):

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


class AllExpenses(Handler):

    """

    This should take dates as well -- for now default ot the past year

    """

    route_strings = set(['GET /api/expenses'])
    route = Handler.check_route_strings

    @Handler.require_login
    def handle(self, req):


        expense_categories = expenses.\
            ExpenseCategories.get_all(self.cw.get_pgconn())


        if req.user and (req.user.email_address == 'rob@216software.com' or\
            req.user.email_address == 'Debby.heinen@gmail.com'):

            return Response.json(dict(
                reply_timestamp=datetime.datetime.now(),
                success=True,
                expense_categories=expense_categories,
                message="People and categories"))



class GetTodayJournalEntry(Handler):

    """

    This gets today's journal entry

    """

    route_strings = set(['GET /api/journal/todays-entry'])
    route = Handler.check_route_strings

    @Handler.require_login
    def handle(self, req):

        pgconn = self.cw.get_pgconn()

        cursor = pgconn.cursor()



        cursor.execute("""

            select * from

            journal_entries

            where person_uuid = %(person_uuid)s
            and inserted::date = now()::date

            order by inserted desc

            limit 1

        """, {'person_uuid':req.user.person_uuid})

        journal_entry = None
        if cursor.rowcount:
            journal_entry = cursor.fetchone()

        return Response.json(dict(
            reply_timestamp=datetime.datetime.now(),
            success=True,
            journal_id=journal_entry.journal_id if journal_entry else None,
            entry=journal_entry.entry if journal_entry else None,
            message="Todays Journal Entry"))


class SaveTodayJournalEntry(Handler):

    """

    This gets today's journal entry

    """

    route_strings = set(['POST /api/journal/todays-entry'])
    route = Handler.check_route_strings

    @Handler.require_login
    def handle(self, req):

        pgconn = self.cw.get_pgconn()

        cursor = pgconn.cursor()
        journal_id = req.json.get('journal_id')

        if journal_id:
            cursor.execute("""

                update journal_entries
                set entry = %(entry)s

                where person_uuid = %(person_uuid)s
                and inserted::date = now()::date

                returning entry, journal_id

            """, {'person_uuid':req.user.person_uuid, 'entry':req.json.get('entry')})


        else:
            cursor.execute("""

                insert into journal_entries
                (entry, person_uuid)
                values

                (%(entry)s, %(person_uuid)s)

                returning entry, journal_id

            """, {'person_uuid':req.user.person_uuid, 'entry':req.json.get('entry')})

        journal_entry = None
        if cursor.rowcount:
            journal_entry = cursor.fetchone()

        return Response.json(dict(
            reply_timestamp=datetime.datetime.now(),
            success=True,
            entry=journal_entry.entry if journal_entry else None,
            journal_id=journal_entry.journal_id,
            message="Saved Todays Journal Entry"))










