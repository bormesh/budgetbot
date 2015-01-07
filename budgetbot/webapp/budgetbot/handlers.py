#vim: set expandtab ts=4 sw=4 filetype=python:

import logging

from budgetbot.webapp.framework.handler import Handler
from budgetbot.webapp.framework.response import Response

from budgetbot.pg import user, expenses

log = logging.getLogger(__name__)

module_template_prefix = 'budgetbot'
module_template_package = 'budgetbot.webapp.budgetbot.templates'

__all__ = ['Splash', 'InsertExpense']

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

class InsertExpense(Handler):

    route_strings = set(['POST /insert-expense'])
    route = Handler.check_route_strings

    def handle(self, req):

        log.info("adding expense new")

        if not req.json:
            return Response.json({'status':'error'})

        log.info("req json is {0}".format(req.json))

        self.insert_expense(req.json['person_id'],
                            req.json['amount'],
                            req.json['expense_date'],
                            req.json['expense_category'],
                            req.json.get('extra_notes'))

        return Response.json({'status':'success'})

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

        """, {'person_id':person_id, 'amount':amount,
               'expense_date':expense_date,
               'expense_category':expense_category,
               'extra_notes':extra_notes})


        return cursor.rowcount




