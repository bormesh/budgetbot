#vim: set expandtab ts=4 sw=4 filetype=python:

import datetime
import logging
import textwrap

import psycopg2

from budgetbot.webapp.framework.handler import Handler
from budgetbot.webapp.framework.response import Response


log = logging.getLogger(__name__)

module_template_prefix = 'shoppinglist'
module_template_package = 'budgetbot.webapp.shoppinglist.templates'

__all__ = ['AllItems', 'InsertShoppingItem', 'RemoveShoppingItem' ]

class AllItems(Handler):

    route_strings = set(['GET /api/shopping-list'])
    route = Handler.check_route_strings


    def handle(self, req):
        pgconn = self.cw.get_pgconn()

        cursor = pgconn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute(textwrap.dedent("""

            select *

            from shopping_list_items

        """))

        return Response.json(dict(
            reply_timestamp=datetime.datetime.now(),
            success=True,
            message="Returning Shopping List",
            items=cursor.fetchall()))


class InsertShoppingItem(Handler):

    route_strings = set(['POST /api/insert-shopping-item'])
    route = Handler.check_route_strings

    def handle(self, req):

        log.info("adding new shopping item")
        expense_uuid = self.insert_expense(req.json['person_id'],
                            req.json['amount'],
                            req.json['expense_date'],
                            req.json['expense_category'],
                            req.json.get('extra_notes'))

        pgconn = self.cw.get_pgconn()

        cursor = pgconn.cursor()

        cursor.execute(textwrap.dedent("""

            insert into shopping_list_items

            (item, shopping_category)

            values

            %(item)s, 'long term'

            returning title, inserted


        """), dict(title=req.json['title']))

        result = cursor.fetchone()

        return Response.json(dict(
            reply_timestamp=datetime.datetime.now(),
            success=True,
            message="Inserted {0}".format(req.json['title']),
            item=dict(result.item)))

class DeleteShoppingItem(Handler):

    route_strings = set(['POST /api/delete-shopping-item'])
    route = Handler.check_route_strings

    def handle(self, req):

        log.info("deleting shopping item")

        if not req.json:
            return Response.json({'success':'false'})

        log.info("req json is {0}".format(req.json))

        cursor = self.cw.get_pgconn().cursor()

        cursor.execute(textwrap.dedent("""

            delete from shopping_list_items

            where item = %(item)s

        """),{'item':req.json['item']})

        return Response.json(dict(
            reply_timestamp=datetime.datetime.now(),
            success=True,
            message="Removed {0}".format(req.json['item'])))





