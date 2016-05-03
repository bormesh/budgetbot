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

__all__ = ['AllLists', 'AllItems', 'AllStores', 'ShoppingListDeets',
    'InsertShoppingItem', 'RemoveShoppingItem', 'InsertShoppingListUser' ]


class AllLists(Handler):

    route_strings = set(['GET /api/shopping-lists'])
    route = Handler.check_route_strings


    @Handler.require_login
    def handle(self, req):
        pgconn = self.cw.get_pgconn()

        cursor = pgconn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute(textwrap.dedent("""

            select *

            from shopping_lists

            where creator_uuid = %(person_uuid)s

        """), {'person_uuid': req.user.person_uuid})

        return Response.json(dict(
            reply_timestamp=datetime.datetime.now(),
            success=True,
            message="Returning Shopping Lists",
            lists=cursor.fetchall()))


class InsertShoppingList(Handler):

    route_strings = set(['POST /api/insert-shopping-list'])
    route = Handler.check_route_strings

    @Handler.require_login
    def handle(self, req):

        log.info("adding new shopping list {0}".format(req.json))
        pgconn = self.cw.get_pgconn()

        cursor = pgconn.cursor()

        cursor.execute(textwrap.dedent("""

            insert into shopping_lists

            (shopping_list_name, store, creator_uuid)

            values

            (%(shopping_list_name)s, %(store)s, %(person_uuid)s)

            returning inserted

        """), dict(shopping_list_name=req.json['shopping_list_name'],
            store=req.json['store'],
            person_uuid=req.user.person_uuid))

        result = cursor.fetchone()

        return Response.json(dict(
            reply_timestamp=datetime.datetime.now(),
            success=True,
            message="Inserted list",
            list_inserted_time=result.inserted))

class ShoppingListDeets(Handler):

    route_strings = set(['GET /api/shopping-list-deets'])
    route = Handler.check_route_strings

    @Handler.require_login
    def handle(self, req):
        pgconn = self.cw.get_pgconn()

        cursor = pgconn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute(textwrap.dedent("""

            select shopping_list_name, store

            from shopping_lists

            where shopping_list_id = %(shopping_list_id)s

        """), {'shopping_list_id': req.args.get('shopping_list_id')})

        return Response.json(dict(
            reply_timestamp=datetime.datetime.now(),
            success=True,
            message="Shopping list deets",
            items=cursor.fetchone()))




class AllItems(Handler):

    route_strings = set(['GET /api/shopping-list'])
    route = Handler.check_route_strings


    @Handler.require_login
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

class AllStores(Handler):

    route_strings = set(['GET /api/all-stores'])
    route = Handler.check_route_strings

    @Handler.require_login
    def handle(self, req):
        pgconn = self.cw.get_pgconn()

        cursor = pgconn.cursor()

        log.info("json req is {0}".format(req.user))

        cursor.execute(textwrap.dedent("""

            select store

            from stores

        """))

        return Response.json(dict(
            reply_timestamp=datetime.datetime.now(),
            success=True,
            message="Shopping list store types",
            stores=[row.store for row in cursor.fetchall()]))


class InsertShoppingItem(Handler):

    route_strings = set(['POST /api/insert-shopping-item'])
    route = Handler.check_route_strings

    @Handler.require_login
    def handle(self, req):

        log.info("adding new shopping item {0}".format(req.json))
        pgconn = self.cw.get_pgconn()

        cursor = pgconn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # IF a user adds an item to a list, we need to make sure
        # They have rights to add that item

        cursor.execute(textwrap.dedent("""

            insert into items

            (item, inserted_by)

            select %(item)s, %(person_uuid)s

            where not exists (
                select item from items where item =  %(item)s)



        """), dict(item=req.json['item'],
            person_uuid=req.user.person_uuid))

        # Then do the actual insert

        cursor.execute(textwrap.dedent("""

            insert into shopping_list_items

            (item, shopping_list_id, inserted_by)

            values

            (%(item)s, %(shopping_list_id)s, %(person_uuid)s)

            returning *

        """), dict(item=req.json['item'],
            shopping_list_id=req.json['shopping_list_id'],
            person_uuid = req.user.person_uuid))

        result = cursor.fetchone()

        return Response.json(dict(
            reply_timestamp=datetime.datetime.now(),
            success=True,
            message="Inserted item",
            item_inserted=result))

class DeleteShoppingItem(Handler):

    route_strings = set(['POST /api/delete-shopping-item'])
    route = Handler.check_route_strings

    @Handler.require_login
    def handle(self, req):

        cursor = self.cw.get_pgconn().cursor()

        cursor.execute(textwrap.dedent("""

            delete from shopping_list_items

            where item = %(item)s

        """),{'item':req.json['item']})

        return Response.json(dict(
            reply_timestamp=datetime.datetime.now(),
            success=True,
            message="Removed item"))


class DeleteShoppingItem(Handler):

    route_strings = set(['POST /api/insert-shopping-list-user'])
    route = Handler.check_route_strings

    @Handler.require_login
    def handle(self, req):

        # TODO: user request must own shopping list


        log.info("connecting shopping list {0} to person {1}".\
            format(req.json.get('shopping_list_id'), req.json.get('person_uuid'))

        cursor = self.cw.get_pgconn().cursor()

        cursor.execute(textwrap.dedent("""

            insert into shopping_lists_people

            (shopping_list_id, person_uuid)

            values

            (%(shopping_list_id)s, %(person_uuid)s)


        """),{'shopping_list_id':req.json['shopping_list_id'],
            req.json['person_uuid']})

        return Response.json(dict(
            reply_timestamp=datetime.datetime.now(),
            success=True,
            message="Added person to shopping list"))








