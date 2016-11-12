"""
    AVM Fritz!BOX SmartHome Client
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Dokumentation zum Login-Verfahren:
    http://www.avm.de/de/Extern/files/session_id/AVM_Technical_Note_-_Session_ID.pdf

    Smart Home Interface:
    http://www.avm.de/de/Extern/files/session_id/AHA-HTTP-Interface.pdf
"""

from __future__ import print_function, division

import logging
import hashlib
from collections import namedtuple
from xml.etree import ElementTree as ET

from requests import Session
try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

from .actor import Actor


logger = logging.getLogger(__name__)
#Device = namedtuple("Device", "deviceid connectstate switchstate")
LogEntry = namedtuple("LogEntry", "date time message hash")


class FritzBox(object):
    """
    Provides easy access to a FritzBOX's SmartHome functions,
    which are poorly documented by AVM...

    A note about SIDs:
     They expire after some time. If you have a long-running daemon,
     you should call login() every 10 minutes or so else you'll get
     nice 403 errors.
    """

    def __init__(self, ip, username, password, use_tls=False):
        if use_tls:
            self.base_url = 'https://' + ip
        else:
            self.base_url = 'http://' + ip
        self.username = username
        self.password = password
        self.sid = None

        self.session = Session()

    def login(self):
        """
        Try to login and set the internal session id.

        Please note:
        - Any failed login resets all existing session ids, even of
          other users.
        - SIDs expire after some time
        """
        response = self.session.get(self.base_url + '/login_sid.lua')
        xml = ET.fromstring(response.text)
        if xml.find('SID').text == "0000000000000000":
            challenge = xml.find('Challenge').text
            url = self.base_url + "/login_sid.lua"
            response = self.session.get(url, params={
                "username": self.username,
                "response": self._calculate_response(challenge, self.password),
            })
            xml = ET.fromstring(response.text)
            sid = xml.find('SID').text
            if xml.find('SID').text == "0000000000000000":
                blocktime = int(xml.find('BlockTime').text)
                exc = Exception("Login failed, please wait {} seconds".format(
                    blocktime
                ))
                exc.blocktime = blocktime
                raise exc
            self.sid = sid
            return sid

    def _calculate_response(self, challenge, password):
        """Calculate response for the challenge-response authentication"""
        to_hash = (challenge + "-" + password).encode("UTF-16LE")
        hashed = hashlib.md5(to_hash).hexdigest()
        return "{0}-{1}".format(challenge, hashed)

    def _homeautoswitch(self, cmd, ain=None):
        """
        Call a switch method.
        Should only be used by internal library functions.
        """
        assert self.sid, "Not logged in"
        params = {
            'switchcmd': cmd,
            'sid': self.sid,
        }
        if ain:
            params['ain'] = ain
        url = self.base_url + '/webservices/homeautoswitch.lua'
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.content.strip()

    # Methods for commands as defined in
    # http://www.avm.de/de/Extern/files/session_id/AHA-HTTP-Interface.pdf
    def get_switch_list(self):
        val = self._homeautoswitch('getswitchlist')
        if val:
            return val.split(',')
        return []

    def get_switch_actors(self):
        """ Get information all switch actors """
        return filter(lambda a: a.actor_id, self.get_actors())

    def set_switch_on(self, actor):
        """Switch the power of a actor ON"""
        return self._homeautoswitch('setswitchon', actor.actor_id)

    def set_switch_off(self, actor):
        """Switch the power of a actor OFF"""
        return self._homeautoswitch('setswitchoff', actor.actor_id)

    def set_switch_toggle(self, actor):
        """Toggle a power switch and return the new state"""
        return self._homeautoswitch('setswitchtoggle', actor.actor_id)

    def get_switch_state(self, actor):
        """ Get the current switch state. """
        val = self._homeautoswitch('getswitchstate', actor.actor_id)
        return int(val) if val.isdigit() else None

    def get_switch_present(self, actor):
        """ Check if the registered actor is currently present (reachable).
        """
        val = self._homeautoswitch('getswitchpresent', actor.actor_id)
        return int(val) if val.isdigit() else None

    def get_switch_power(self, actor):
        """ Returns the current power usage in milliWatts.
        Attention: Returns None if the value can't be queried or is unknown.
        """
        val = self._homeautoswitch('getswitchpower', actor.actor_id)
        return int(val) if val.isdigit() else None

    def get_switch_energy(self, actor):
        """ Returns the consumed energy since the start of the statistics in Wh.
        Attention: Returns None if the value can't be queried or is unknown.
        """
        val = self._homeautoswitch('getswitchenergy', actor.actor_id)
        return int(val) if val.isdigit() else None

    def get_switch_name(self, actor):
        return self._homeautoswitch('getswitchname', actor.actor_id)

    def get_device_list_infos(self):
        """ Returns a list of Actor objects for querying SmartHome devices.
        This is currently the only working method for getting temperature data.
        """
        devices = self._homeautoswitch('getdevicelistinfos')
        xml = ET.fromstring(devices)

        actors = []
        for device in xml.findall('device'):
            actors.append(Actor(device_xml=device))

        return actors

    def get_temperature(self):
        """ Returns the current environment temperature.
        Attention: Returns None if the value can't be queried or is unknown.
        """
        val = self._homeautoswitch('gettemperature', actor.actor_id)
        return float(val)/10 if val.isdigit() else None


    # Helpers / "own" methods
    def get_actor_by_ain(self, ain):
        """
        Return a actor identified by it's ain or return None
        """
        for actor in self.get_actors():
            if actor.actor_id == ain:
                return actor

    def get_actors(self):
        return self.get_device_list_infos()

    def get_consumption(self, actor, timerange='10'):
        """
        Return all available energy consumption data for the device.
        You need to divice watt_values by 100 and volt_values by 1000
        to get the "real" values.

        :return: dict
        """
        tranges = ("10", "24h", "month", "year")
        if timerange not in tranges:
            raise ValueError(
                "Unknown timerange. Possible values are: {0}".format(tranges)
            )

        url = self.base_url + "/net/home_auto_query.lua"
        response = self.session.get(url, params={
            'sid': self.sid,
            'command': 'EnergyStats_{0}'.format(timerange),
            'id': actor.device_id,
            'xhr': 0,
        })
        response.raise_for_status()

        data = response.json()
        result = {}

        # Single result values
        values_map = {
            'MM_Value_Amp': 'mm_value_amp',
            'MM_Value_Power': 'mm_value_power',
            'MM_Value_Volt': 'mm_value_volt',

            'EnStats_average_value': 'enstats_average_value',
            'EnStats_max_value': 'enstats_max_value',
            'EnStats_min_value': 'enstats_min_value',
            'EnStats_timer_type': 'enstats_timer_type',

            'sum_Day': 'sum_day',
            'sum_Month': 'sum_month',
            'sum_Year': 'sum_year',
        }
        for avm_key, py_key in values_map.items():
            result[py_key] = int(data[avm_key])

        # Stats counts
        count = int(data["EnStats_count"])
        watt_values = [None for i in range(count)]
        volt_values = [None for i in range(count)]
        for i in range(1, count + 1):
            watt_values[i - 1] = int(data["EnStats_watt_value_{}".format(i)])
            volt_values[i - 1] = int(data["EnStats_volt_value_{}".format(i)])

        result['watt_values'] = watt_values
        result['volt_values'] = volt_values

        return result

    def get_logs(self):
        """
        Return the system logs since the last reboot.
        """
        assert BeautifulSoup, "Please install bs4 to use this method"

        url = self.base_url + "/system/syslog.lua"
        response = self.session.get(url, params={
            'sid': self.sid,
            'stylemode': 'print',
        })
        response.raise_for_status()

        entries = []
        tree = BeautifulSoup(response.text)
        rows = tree.find('table').find_all('tr')
        for row in rows:
            columns = row.find_all("td")
            date = columns[0].string
            time = columns[1].string
            message = columns[2].find("a").string

            merged = "{} {} {}".format(date, time, message.encode("UTF-8"))
            msg_hash = hashlib.md5(merged).hexdigest()
            entries.append(LogEntry(date, time, message, msg_hash))
        return entries
