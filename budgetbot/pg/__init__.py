# vim: set expandtab ts=4 sw=4 filetype=python fileencoding=utf8:

import abc
import copy
import datetime
import logging
import os
import re
import textwrap
import urllib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

log = logging.getLogger(__name__)

class RelationWrapper(object):

    bad_textsearch_chars = u"():\\!&"

    @classmethod
    def to_tsquery_string(cls, s):

        bad_chars = dict((ord(c), None) for c in cls.bad_textsearch_chars)

        tsquery_string = ' & '.join(re.split(
            '\s+',
            unicode(s.strip()).translate(bad_chars)))

        return tsquery_string

    @property
    def __jsondata__(self):
        return self.__dict__

class UpDown(object):

    __metaclass__ = abc.ABCMeta

    def __repr__(self):

        return "<{0}.{1} {2} ({3})>".format(
            self.__class__.__module__,
            self.__class__.__name__,
            self.filename,
            self.pk)

    @abc.abstractproperty
    def pk(self):
        raise NotImplementedError("Sorry, you must define me!")

    def get_current_status(self, pgconn):

        qry = textwrap.dedent("""
            select ({0}.*)::{0} as h
            from {0}
            where {1} = %(pk)s
            and current_timestamp <@ {0}.effective
            """).format(
                self.history_table_name,
                self.pk_column_name)

        cursor = pgconn.cursor()

        cursor.execute(qry, dict( pk=self.pk))

        if cursor.rowcount:
            self.current_status = cursor.fetchone().h
            return self.current_status

        else:
            raise KeyError("Sorry, no {0} with PK {1} found!".format(
                self.history_table_name,
                self.pk))

    def update_status(self, pgconn, new_status, who_did_it):

        qry = textwrap.dedent("""
            insert into {0}
            ({1}, status, who_did_it)
            values
            (%(pk)s, %(status)s, %(who_did_it)s)
            """.format(
                self.history_table_name,
                self.pk_column_name))

        cursor = pgconn.cursor()

        cursor.execute(qry,
            dict(
                pk=self.pk,
                status=new_status,
                who_did_it=who_did_it))

        log.info("Just updated status for {0} to {1}".format(self, new_status))

    table_name = "SUBCLASS MUST DEFINE"
    history_table_name = "SUBCLASS MUST DEFINE"
    pk_column_name = "SUBCLASS MUST DEFINE"

    @classmethod
    def by_filename(cls, pgconn, filename):

        if cls.table_name == "SUBCLASS MUST DEFINE":
            raise ValueError("Sorry, I need a table name!")

        else:

            qry = textwrap.dedent("""
                select ({0}.*)::{0} as f
                from {0}
                where filename = %(filename)s
                """).format(cls.table_name)

            cursor = pgconn.cursor()

            cursor.execute(qry, dict(filename=filename))

            if cursor.rowcount:
                return cursor.fetchone().f

            else:
                raise KeyError("No MCR file {0} found!".format(filename))

    @classmethod
    def insert(cls, pgconn, filename, uploaded_by):

        qry = textwrap.dedent("""
            insert into {0}
            (filename, uploaded_by)
            select %(filename)s, %(uploaded_by)s
            where not exists
            (
                select *
                from {0}
                where filename = %(filename)s
            )
            returning ({0}.*)::{0} as f
            """).format(cls.table_name)

        cursor = pgconn.cursor()

        cursor.execute(qry, dict(
            filename=filename,
            uploaded_by=uploaded_by))

        if cursor.rowcount:
            f = cursor.fetchone().f

            log.info("Just inserted file {0} as {1}".format(
                filename,
                f))

            return f

        else:
            raise KeyError(
                "Sorry, already uploaded {0}!".format(filename))

    def retrieve_locally(self):

        if not self.download_url:
            raise ValueError("Sorry, I need a download URL!")

        elif self.local_copy:
            raise ValueError("We already have a local copy!")

        else:

            urllib.urlretrieve(
                self.download_url,
                "/tmp/{0}".format(self.filename))

            self.local_copy = "/tmp/{0}".format(self.filename)

            log.info("Just stored a local copy of {0} here: {1}".format(
                self,
                self.local_copy))

            return self

    @classmethod
    def by_current_status(cls, pgconn, current_status):

        qry = textwrap.dedent("""
            select ({0}.*)::{0} as f,
            ({1}.*)::{1} as h

            from {0}

            join {1}
            on {0}.{2} = {1}.{2}
            and current_timestamp <@ {1}.effective
            and {1}.status = %(current_status)s

            order by {0}.inserted
            """).format(
                cls.table_name,
                cls.history_table_name,
                cls.pk_column_name)

        cursor = pgconn.cursor()

        cursor.execute(qry, dict(current_status=current_status))

        for row in cursor:

            f, h = row
            f.current_status = h

            yield f


    @classmethod
    def select(cls, pgconn, offset, limit):

        qry = textwrap.dedent("""
            select ({0}.*)::{0} as f,
            ({1}.*)::{1} as h

            from {0}

            join {1}
            on {0}.{2} = {1}.{2}
            and current_timestamp <@ {1}.effective

            order by {0}.inserted desc
            offset %(offset)s
            limit %(limit)s
            """).format(cls.table_name, cls.history_table_name,
            cls.pk_column_name)

        cursor = pgconn.cursor()

        cursor.execute(
            qry,
            dict(offset=offset, limit=limit))

        for row in cursor:
            f, h = row
            f.current_status = h
            yield f

    @staticmethod
    def notify_listener(listener_channel, pgconn, payload):

        qry = textwrap.dedent("""
            notify {0}, %(payload)s
            """).format(listener_channel)

        cursor = pgconn.cursor()

        cursor.execute(qry, dict(payload=payload))

        log.info("Notified {0}, payload {1}".format(
            listener_channel,
            payload))

    @staticmethod
    def clean_up_row_keys(row):

        """
        Insert new key / value pairs into dictionary row.

        >>> row = {"  abc  ": 99}

        >>> "abc" in row
        False

        >>> MCRFile.clean_up_row_keys(row)
        {'abc': 99, '  abc  ': 99}

        >>> "abc" in row
        True

        """

        for k in copy.copy(row):

            clean_k = k.strip()

            if clean_k not in row:
                row[clean_k] = row[k]

            if clean_k.lower() not in row:
                row[clean_k.lower()] = row[k]

        return row

    @staticmethod
    def clean_up_numeric_value(s):

        if s in set(["$-", "#N/A"]):
            return

        else:
            s2 = s.strip().replace("$", "").replace("%", "").replace(",", "").replace("-", "")

            if s2:
                return s2



# Normally, imports go at the top, but since I want stuff in the pg
# modules to import this RelationWrapper.

from . import people
from . import sessions
