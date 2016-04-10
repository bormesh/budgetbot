# vim: set expandtab ts=4 sw=4 filetype=python:

import copy
import logging
import os
import textwrap
import urllib
import uuid

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import itsdangerous
import psycopg2.extras

from budgetbot import configwrapper

log = logging.getLogger(__name__)

class PersonFactory(psycopg2.extras.CompositeCaster):

    def make(self, values):
        d = dict(zip(self.attnames, values))
        return Person(**d)


class Person(object):

    def __init__(self, person_uuid, email_address, salted_hashed_password,
        person_status, display_name, is_superuser,
        inserted,
        updated):

        self.person_uuid = person_uuid
        self.email_address = email_address
        self.salted_hashed_password = salted_hashed_password
        self.person_status = person_status
        self.display_name = display_name
        self.is_superuser = is_superuser
        self.inserted = inserted
        self.updated = updated

    def __repr__(self):
        return '<{0}.{1} ({2}:{3}) at 0x{4:x}>'.format(
            self.__class__.__module__,
            self.__class__.__name__,
            self.person_uuid,
            self.display_name,
            id(self))

    def __eq__(self, other):
        return self.person_uuid == getattr(other, 'person_uuid', -1)

    @classmethod
    def insert(cls, pgconn, email_address, raw_password,
        display_name):

        """

        Insert a new person

        """

        cursor = pgconn.cursor()

        cursor.execute("""

            insert into people

            (email_address, display_name,
             salted_hashed_password, person_status)

            values

            (
             %(email_address)s, %(display_name)s,
             crypt(%(raw_password)s, gen_salt('bf')),
             'confirmed'
            )

            returning (people.*)::people as person

        """,{'email_address':email_address, 'display_name':display_name,
             'raw_password':raw_password })

        new_person = cursor.fetchone().person

        return new_person



    @classmethod
    def by_email_address(cls, pgconn, email_address):

        cursor = pgconn.cursor()

        cursor.execute(textwrap.dedent("""
            select (p.*)::people as p
            from people p
            where email_address = %(email_address)s
            """), {'email_address': email_address})

        if cursor.rowcount:
            return cursor.fetchone().p

        else:
            raise KeyError("Sorry, couldn't find {0}!".format(
                email_address))


    @classmethod
    def select_all(cls, pgconn, offset=0, limit=10, sort='asc'):

        cursor = pgconn.cursor()

        cursor.execute(textwrap.dedent("""
            select (p.*)::people as p
            from people p
            order by display_name
            """))

        for row in cursor:
            yield row.p

    @classmethod
    def select_count(cls, pgconn):

        cursor = pgconn.cursor()

        cursor.execute(textwrap.dedent("""
            select count(*)
            from people
            """))

        return cursor.fetchone().count


    @property
    def __jsondata__(self):

        d = copy.copy(self.__dict__)

        return d


    @classmethod
    def by_person_uuid(cls, pgconn, person_uuid):

        cursor = pgconn.cursor()

        cursor.execute(textwrap.dedent("""
            select (p.*)::people as p
            from people p
            where person_uuid = %(person_uuid)s
            """), {'person_uuid': person_uuid})

        if cursor.rowcount:
            return cursor.fetchone().p

    def send_reset_password_email(self, cw):

        signer = itsdangerous.URLSafeTimedSerializer(cw.app_secret)

        tmpl = cw.j.get_template("emailtemplates/password-reset.html")

        html_email = MIMEText(tmpl.render({
            "email_address": self.email_address,
            "host": cw.host,
            "web_host": cw.web_host,

            "payload": signer.dumps({
                "email_address": self.email_address}),
            }
        ), "html")

        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Password Reset for {0}".format(self.display_name)
        msg['From'] = "streamliner@{0}".format(cw.host)
        msg['To'] = self.email_address

        msg.attach(html_email)

        smtp_connection = cw.make_smtp_connection()

        smtp_connection.sendmail(
            "streamliner@{0}".format(cw.host),
            [self.email_address],
            msg.as_string())

        log.info("Just sent confirm-signup email")

    def update_my_password(self, pgconn, current_password,
        new_password):

        cursor = pgconn.cursor()

        cursor.execute(textwrap.dedent("""
            update people

            set salted_hashed_password = crypt(
                %(new_password)s, gen_salt('bf'))

            where person_uuid = %(person_uuid)s

            and salted_hashed_password = crypt(
                %(current_password)s,
                salted_hashed_password)

            returning (people.*)::people as p
            """), dict(
                new_password=new_password,
                person_uuid=self.person_uuid,
                current_password=current_password))

        if cursor.rowcount:
            return cursor.fetchone().p

        else:
            raise KeyError("Sorry, no person with UUID {0}"
                " and that current password found!".format(
                self.person_uuid))

    def update_password(self, pgconn, new_password):

        cursor = pgconn.cursor()

        cursor.execute(textwrap.dedent("""
            update people

            set salted_hashed_password = crypt(
                %(new_password)s, gen_salt('bf'))

            where person_uuid = %(person_uuid)s

            returning (people.*)::people as p
            """), dict(
                new_password=new_password,
                person_uuid=self.person_uuid))

        if cursor.rowcount:
            return cursor.fetchone().p

        else:
            raise KeyError("Sorry, no person with UUID {0} found!".format(
                self.person_uuid))

    def update_my_status(self, pgconn, new_status):

        cursor = pgconn.cursor()

        cursor.execute(textwrap.dedent("""
            update people
            set person_status = %(person_status)s
            where person_uuid = %(person_uuid)s
            returning (people.*)::people as p
            """), {'person_status':new_status,
                'person_uuid':self.person_uuid})

        if cursor.rowcount:
            return cursor.fetchone().p

        else:
            raise KeyError("Sorry, bad status {0}!".format(new_status))

    def update_my_group(self, pgconn, new_group):

        cursor = pgconn.cursor()

        cursor.execute(textwrap.dedent("""
            update people
            set group_title = %(group_title)s
            where person_uuid = %(person_uuid)s
            returning (people.*)::people as p
            """), {'group_title':new_group,
                'person_uuid':self.person_uuid})

        if cursor.rowcount:
            return cursor.fetchone().p

        else:
            raise KeyError("Sorry, bad group {0}!".format(new_group))


