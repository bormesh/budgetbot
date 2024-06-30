# vim: set expandtab ts=4 sw=4 filetype=python fileencoding=utf8:

import logging
import pprint

import clepy
from horsemeat import fancyjsondumps
from horsemeat.webapp import response


from budgetbot import configwrapper

log = logging.getLogger(__name__)

class Response(response.Response):


    configwrapper = configwrapper
    fancyjsondumps = fancyjsondumps

    """
    Add stuff here that is specific to the budgetbot response.
    """

    # TODO: Move into horsemeat
    @classmethod
    def csv_file(cls, filelike, filename, FileWrap):

        """

        Here's an example usage::

            query = textwrap.dedent('''
                copy (
                    select *
                    from blah
                )
                to stdout with csv header
                ''')

            tf = tempfile.NamedTemporaryFile()

            cursor.copy_expert(query, tf)

            return Response.csv_file(filelike=tf,
                                     filename='csv-data',
                                     FileWrap=req.environ['wsgi.file_wrapper'])

        """

        block_size = 4096

        return cls(
            '200 OK',
            [('Content-Type', 'text/csv'),
             ('Content-Disposition', 'attachment; filename={0}'.format(filename))],
            FileWrap(filelike, block_size))

    # TODO: Move into horsemeat
    @property
    def body(self):
        return self._body


    # TODO: Move into horsemeat
    @body.setter
    def body(self, val):

        """
        If the body isn't wrapped in a list, I'll wrap it in a list.

        (Only if it's not a file wrapper)
        """

        from gunicorn.http.wsgi import FileWrapper

        if not isinstance(val, FileWrapper):
            self._body = clepy.listmofize(val)
        else:
            self._body = val


    @classmethod
    def json(cls, data, status='200'):
        """
        Matt is overwriting the horsemeat Response.json classmethod
        here.

        Future versions of horsemeat will have this code, but right now,
        I don't want to bump sofaconcerts up to a new version of
        horsemeat because that might introduce all sorts of weird little
        issues.

        """

        log.info("IN JSON response")

        if status == '400':
            response_status = '400 Bad Request'
        elif status == '404':
            response_status = '400 Not Found'
        else:
            response_status = '200 OK'

        s = bytes(cls.fancyjsondumps(data), 'utf-8')
        json_response = cls(
            response_status,
            [
                ('Content-Type', 'application/json'),
                ('Content-Length', str(len(s))),
            ],
            s)

        return json_response


