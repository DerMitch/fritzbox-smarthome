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

    def __init__(self, fritzbox, device):
        self.box = fritzbox

        self.actor_id = device.attrib['identifier']
        self.device_id = device.attrib['id']
        self.name = device.find('name').text
        self.fwversion = device.attrib['fwversion']
        self.productname = device.attrib['productname']
        self.manufacturer = device.attrib['manufacturer']
        self.functionbitmask = int(device.attrib['functionbitmask'])

        self.has_powermeter = self.functionbitmask & (1 << 7) > 0
        self.has_temperature = self.functionbitmask & (1 << 8) > 0
        self.has_switch = self.functionbitmask & (1 << 9) > 0
        self.has_heating_controller = self.functionbitmask & (1 << 6) > 0

        self.temperature = 0.0
        if self.has_temperature:
            if device.find("temperature").find("celsius").text is not None:
                self.temperature = int(device.find("temperature").find("celsius").text) / 10
            else:
                logger.warn("Actor " + self.name + " seems offline. Returning None as temperature.")
                self.temperature=None

        self.target_temperature = 0.0
        self.target_temperature = 0.0
        self.battery_low = True
        if self.has_heating_controller:
            hkr = device.find("hkr")
            if hkr is not None:
                for child in hkr:
                    if child.tag == 'tist':
                        self.temperature = self.__get_temp(child.text)
                    elif child.tag == 'tsoll':
                        self.target_temperature = self.__get_temp(child.text)
                    elif child.tag == 'batterylow':
                        self.battery_low = (child.text == '1')

    def switch_on(self):
        """
        Set the power switch to ON.
        """
        return self.box.set_switch_on(self.actor_id)

    def switch_off(self):
        """
        Set the power switch to OFF.
        """
        return self.box.set_switch_off(self.actor_id)

    def get_state(self):
        """
        Get the current switch state.
        """
        return bool(
            int(self.box.homeautoswitch("getswitchstate", self.actor_id))
        )

    def get_present(self):
        """
        Check if the registered actor is currently present (reachable).
        """
        return bool(
            int(self.box.homeautoswitch("getswitchpresent", self.actor_id))
        )

    def get_power(self):
        """
        Returns the current power usage in milliWatts.
        Attention: Returns None if the value can't be queried or is unknown.
        """
        value = self.box.homeautoswitch("getswitchpower", self.actor_id)
        return int(value) if value.isdigit() else None

    def get_energy(self):
        """
        Returns the consumed energy since the start of the statistics in Wh.
        Attention: Returns None if the value can't be queried or is unknown.
        """
        value = self.box.homeautoswitch("getswitchenergy", self.actor_id)
        return int(value) if value.isdigit() else None

    def get_temperature(self):
        """
        Returns the current environment temperature.
        Attention: Returns None if the value can't be queried or is unknown.
        """
        #raise NotImplementedError("This should work according to the AVM docs, but don't...")
        value = self.box.homeautoswitch("gettemperature", self.actor_id)
        if value.isdigit():
            self.temperature = float(value)/10
        else:
            self.temperature = None
        return self.temperature

    def __get_temp(self, value):
        # Temperature is send from fritz.box a little weird
        if value.isdigit():
            value = float(value)
            if value == 253:
                return 0
            elif value == 254:
                return 30
            else:
                return value / 2
        else:
            return None

    def get_target_temperature(self):
        """
        Returns the actual target temperature.
        Attention: Returns None if the value can't be queried or is unknown.
        """
        value = self.box.homeautoswitch("gethkrtsoll", self.actor_id)
        self.target_temperature = self.__get_temp(value)
        return self.target_temperature

    def set_temperature(self, temp):
        """
        Sets the temperature in celcius
        """

        # Temperature is send to fritz.box a little weird
        param = 16 + ( ( temp - 8 ) * 2 )
        if param < 16:
            param = 253
            logger.info("Actor " + self.name + ": Temperature control set to off")
        elif param >= 56:
            param = 254
            logger.info("Actor " + self.name + ": Temperature control set to on")
        else:
            logger.info("Actor " + self.name + ": Temperature control set to " + str(temp))

        return self.box.homeautoswitch("sethkrtsoll", self.actor_id, param)
        
    def get_consumption(self, timerange="10"):
        """
        Return the energy report for the device.
        """
        return self.box.get_consumption(self.device_id, timerange)

    def __repr__(self):
        return u"<Actor {}>".format(self.name)
