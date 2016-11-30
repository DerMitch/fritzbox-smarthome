"""
    AVM SmartHome Actor
    ~~~~~~~~~~~~~~~~~~~
"""

import logging
logger = logging.getLogger(__name__)

class Actor(object):
    """
    Represents a single SmartHome actor.
    You usally don't create that class yourself, use FritzBox.get_actors
    instead.
    """
    def __init__(self, device_xml):
        self.actor_id = device_xml.attrib['identifier']
        self.device_id = device_xml.attrib['id']
        self.name = device_xml.find('name').text
        self.fwversion = device_xml.attrib['fwversion']
        self.productname = device_xml.attrib['productname']
        self.manufacturer = device_xml.attrib['manufacturer']

        self.functionbitmask = int(device_xml.attrib['functionbitmask'])
        self.has_hkr = self.functionbitmask & (1 << 6) > 0
        self.has_powermeter = self.functionbitmask & (1 << 7) > 0
        self.has_temperature = self.functionbitmask & (1 << 8) > 0
        self.has_switch = self.functionbitmask & (1 << 9) > 0
        self.hast_dect_repeater = self.functionbitmask & (1 << 10) > 0

        self.temperature = 0.0
        if self.has_temperature:
            if device_xml.find("temperature").find("celsius").text is not None:
                self.temperature = float(device_xml.find("temperature").find("celsius").text) / 10.0
            else:
                logger.warn("Actor " + self.name + " seems offline. Returning None as temperature.")
                self.temperature=None

    def __repr__(self):
        return u'<Actor {}>'.format(repr(self.name))
