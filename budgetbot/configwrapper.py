# vim: set expandtab ts=4 sw=4 filetype=python:

import logging
import warnings

import jinja2
import psycopg2.extras

from horsemeat import configwrapper

log = logging.getLogger(__name__)

class ConfigWrapper(configwrapper.ConfigWrapper):

    # Where are the config files?
    configmodule = "budgetbot.yamlfiles"

    @property
    def dispatcher_class(self):

        from budgetbot.webapp.framework.dispatcher import Dispatcher
        return Dispatcher

    def get_mailgun_host(self):

        return self.config_dictionary['mailgun_config']['HOST']

    def get_mailgun_api_key(self):

        return self.config_dictionary['mailgun_config']['API_KEY']

    def register_composite_types(self, pgconn):

        from budgetbot.pg.people import PersonFactory
        from budgetbot.pg.expenses import ExpenseCategoryFactory, \
                                          ExpenseCategoriesDenormalizedFactory, \
                                         ExpenseFactory

        psycopg2.extras.register_composite('people', pgconn,
          factory=PersonFactory)


        from budgetbot.pg.sessions import SessionFactory

        psycopg2.extras.register_composite(
            'webapp_sessions',
            pgconn,
            factory=SessionFactory)


        psycopg2.extras.register_composite('expenses', pgconn,
          factory=ExpenseFactory)

        psycopg2.extras.register_composite('expense_categories', pgconn,
          factory=ExpenseCategoryFactory)

        psycopg2.extras.register_composite('expense_categories_denormalized', pgconn,
          factory=ExpenseCategoriesDenormalizedFactory)


        log.info('Just registered composite types in psycopg2')

        return pgconn


    def add_more_stuff_to_jinja2_globals(self):

        j = self.get_jinja2_environment()

        j.add_extension('jinja2.ext.do')

        j.loader.mapping['emailtemplates'] = jinja2.PackageLoader(
            'budgetbot',
            'emailtemplates')

