# vim: set expandtab ts=4 sw=4 filetype=python fileencoding=utf8:

import logging
import re
import requests
import textwrap

from budgetbot.webapp.framework.handler import Handler
from budgetbot.webapp.framework.response import Response

__all__ = ['PickupPage', 'SendNewGiftGram','Inbox', 'Sent']

log = logging.getLogger(__name__)

module_template_prefix = 'mockups'
module_template_package = 'budgetbot.webapp.mockups.templates'


class BusTimes(Handler):

    route_strings = set(['GET /bus'])

    route = Handler.check_route_strings

    def handle(self, req):

        return Response.tmpl('mockups/bus.html')

class BusTimesJSON(Handler):

    route_strings = set(['GET /bus-times'])

    route = Handler.check_route_strings

    def handle(self, req):

        # Cedar and Grandview East
        response = requests.post(
            'http://nextconnect.riderta.com/Arrivals.aspx/getStopTimes',
            data = '{"routeID": "149","directionID":"3","stopID":"9081", "useArrivalTimes":"false"}',
            headers={'Content-Type': ' application/json'})

        homeeast = response.json()['d']['stops'][0]['crossings']

        log.debug(response.json())


        response = requests.post(
            'http://nextconnect.riderta.com/Arrivals.aspx/getStopTimes',
            data = '{"routeID": "103","directionID":"3","stopID":"9405", "useArrivalTimes":"false"}',
            headers={'Content-Type': ' application/json'})

        log.debug(response.json())

        # It's possible for crossings to be null

        [homeeast.append(x) for x in \
             response.json()['d']['stops'][0]['crossings']]


        homedowntown = []

        response = requests.post(
            'http://nextconnect.riderta.com/Arrivals.aspx/getStopTimes',
            data = '{"routeID": "103","directionID":"14","stopID":"9411", "useArrivalTimes":"false"}',
            headers={'Content-Type': ' application/json'})

        [homedowntown.append(x) for x in \
             response.json()['d']['stops'][0]['crossings']]

        response = requests.post(
            'http://nextconnect.riderta.com/Arrivals.aspx/getStopTimes',
            data = '{"routeID": "149","directionID":"14","stopID":"10838", "useArrivalTimes":"false"}',
            headers={'Content-Type': ' application/json'})

        [homedowntown.append(x) for x in \
             response.json()['d']['stops'][0]['crossings']]



        return Response.json({'success':'true',
        'homedowntown':homedowntown,
        'homeeast':homeeast})


