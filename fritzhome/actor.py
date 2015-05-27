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

    def __init__(self, fritzbox, actor_id, device_id, name, fwversion,
                       productname, manufacturer):
        self.box = fritzbox
        self.actor_id = actor_id
        self.device_id = device_id
        self.name = name
        self.fwversion = fwversion
        self.productname = productname
        self.manufacturer = manufacturer

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
            self.box.homeautoswitch("getswitchstate", self.actor_id)
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
        """
        value = self.box.homeautoswitch("getswitchpower", self.actor_id)
        return int(value) if value.isdigit() else None

    def get_energy(self):
        """
        Returns the consumed energy since the start of the statistics in Wh.
        """
        value = self.box.homeautoswitch("getswitchenergy", self.actor_id)
        return int(value) if value.isdigit() else None

    def get_consumption(self, timerange="10"):
        """
        Return the energy report for the device.
        """
        return self.box.get_consumption(self.device_id, timerange)

    def __repr__(self):
        return u"<Actor {}>".format(self.name)
