"""
    AVM SmartHome Actor
    ~~~~~~~~~~~~~~~~~~~
"""


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

        self.temperature = 0.0
        if self.has_temperature:
            self.temperature = int(device.find("temperature").find("celsius").text) / 10

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
            int(
                self.box.homeautoswitch("getswitchstate", self.actor_id)
            )
        )

    def get_present(self):
        """
        Check if the registered actor is currently present (reachable).
        """
        return bool(
            self.box.homeautoswitch("getswitchpresent", self.actor_id)
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
        raise NotImplementedError("This should work according to the AVM docs, but don't...")
        value = self.box.homeautoswitch("gettemperature", self.actor_id)
        return int(value) if value.isdigit() else None

    def get_consumption(self, timerange="10"):
        """
        Return the energy report for the device.
        """
        return self.box.get_consumption(self.device_id, timerange)

    def __repr__(self):
        return u"<Actor {}>".format(self.name)
