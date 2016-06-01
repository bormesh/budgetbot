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
    'ShoppingListUsers', 'InsertShoppingItem', 'InsertShoppingList',
    'DeleteShoppingList',
    'DeleteShoppingItem', 'InsertShoppingListUser' ]


class AllLists(Handler):

    route_strings = set(['GET /api/shopping-lists'])
    route = Handler.check_route_strings


    @Handler.require_login
    def handle(self, req):
        pgconn = self.cw.get_pgconn()

        cursor = pgconn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute(textwrap.dedent("""

            select *

            from shopping_lists sl

            where creator_uuid = %(person_uuid)s

            and removed = false

        """), {'person_uuid': req.user.person_uuid})

        my_lists = cursor.fetchall()

        cursor.execute(textwrap.dedent("""

            select *

            from shopping_lists sl

            join shopping_lists_people slp
            on slp.shopping_list_id = sl.shopping_list_id

            where

            slp.person_uuid = %(person_uuid)s

            and sl.removed = false

        """), {'person_uuid': req.user.person_uuid})

        shared_with_me = cursor.fetchall()

        return Response.json(dict(
            reply_timestamp=datetime.datetime.now(),
            success=True,
            message="Returning Shopping Lists",
            shared_lists=shared_with_me,
            lists=my_lists))


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

            returning shopping_list_id

        """), dict(shopping_list_name=req.json['shopping_list_name'],
            store=req.json['store'],
            person_uuid=req.user.person_uuid))

        result = cursor.fetchone()

        return Response.json(dict(
            reply_timestamp=datetime.datetime.now(),
            success=True,
            message="Inserted list",
            shopping_list_id=result.shopping_list_id))

class DeleteShoppingList(Handler):

    route_strings = set(['POST /api/delete-shopping-list'])
    route = Handler.check_route_strings

    @Handler.require_login
    def handle(self, req):

        log.info("deleting shopping list {0}".format(req.json))
        pgconn = self.cw.get_pgconn()

        cursor = pgconn.cursor()

        cursor.execute(textwrap.dedent("""

            update shopping_lists

            set removed = true

            where shopping_list_id = %(shopping_list_id)s

            returning shopping_list_id

        """), dict(shopping_list_id=req.json['shopping_list_id']))

        result = cursor.fetchone()

        return Response.json(dict(
            reply_timestamp=datetime.datetime.now(),
            success=True,
            message="Removed list",
            shopping_list_id=result.shopping_list_id))




class ShoppingListDeets(Handler):

    route_strings = set(['GET /api/shopping-list-deets'])
    route = Handler.check_route_strings

    @Handler.require_login
    def handle(self, req):
        pgconn = self.cw.get_pgconn()

        log.debug(req.wz_req.args)

        cursor = pgconn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute(textwrap.dedent("""

            select shopping_list_name, store

            from shopping_lists

            where shopping_list_id = %(shopping_list_id)s

        """), {'shopping_list_id': req.wz_req.args.get('shopping_list_id')})

        return Response.json(dict(
            reply_timestamp=datetime.datetime.now(),
            success=True,
            message="Shopping list deets",
            deets=cursor.fetchone()))


class ShoppingListUsers(Handler):

    route_strings = set(['GET /api/shopping-list-users'])
    route = Handler.check_route_strings

    @Handler.require_login
    def handle(self, req):
        pgconn = self.cw.get_pgconn()

        log.debug(req.wz_req.args)

        cursor = pgconn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute(textwrap.dedent("""

            select p.email_address, p.display_name, p.person_uuid

            from shopping_lists_people slp
            join people p on p.person_uuid = slp.person_uuid

            where slp.shopping_list_id = %(shopping_list_id)s

        """), {'shopping_list_id': req.wz_req.args.get('shopping_list_id')})

        return Response.json(dict(
            reply_timestamp=datetime.datetime.now(),
            success=True,
            message="Shopping list deets",
            people=cursor.fetchall()))




class AllItems(Handler):

    route_strings = set(['GET /api/shopping-list-items'])
    route = Handler.check_route_strings


    @Handler.require_login
    def handle(self, req):
        pgconn = self.cw.get_pgconn()

        # TODO -- Make sure that user has access to shopping list

        cursor = pgconn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute(textwrap.dedent("""

            select *

            from shopping_list_items

            where shopping_list_id = %(shopping_list_id)s

        """), {'shopping_list_id': req.wz_req.args.get('shopping_list_id')})

        return Response.json(dict(
            reply_timestamp=datetime.datetime.now(),
            success=True,
            message="Returning Shopping List Items",
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

        # TODO Make sure we have rights to delete this item

        cursor.execute(textwrap.dedent("""

            delete from shopping_list_items

            where item = %(item)s

        """),{'item':req.json['item']})

        return Response.json(dict(
            reply_timestamp=datetime.datetime.now(),
            success=True,
            message="Removed item"))


class InsertShoppingListUser(Handler):

    route_strings = set(['POST /api/insert-shopping-list-user'])
    route = Handler.check_route_strings

    @Handler.require_login
    def handle(self, req):

        # TODO: user request must own shopping list


        log.info("connecting shopping list {0} to person {1}".\
            format(req.json.get('shopping_list_id'),
            req.json.get('person_uuid')))

        cursor = self.cw.get_pgconn().cursor()

        cursor.execute(textwrap.dedent("""

            insert into shopping_lists_people

            (shopping_list_id, person_uuid)

            values

            (%(shopping_list_id)s, %(person_uuid)s)


            """), dict(shopping_list_id=req.json['shopping_list_id'],
                person_uuid=req.json['person_uuid']))

        return Response.json(dict(
            reply_timestamp=datetime.datetime.now(),
            success=True,
            message="Added person to shopping list"))








