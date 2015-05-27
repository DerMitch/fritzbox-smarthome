"""
    Fritz!BOX Webinterface Parser

"""

from collections import namedtuple
from HTMLParser import HTMLParser


DeviceInfo = namedtuple("DeviceInfo", "actor_id device_id name")


class HomeAutoOverviewParser(HTMLParser):
    """
    This class parses the table returned by home_auto_overview
    and creates a list of DeviceInfo objects.
    """
    def __init__(self):
        HTMLParser.__init__(self)

        # State while parsing
        self.capture = None
        self.device_id = None
        self.name = None

        # Result
        self.actors = []

        # Since one of the last updates, the columns were changed:
        # There is now a temperature column (c3), but the AIN is gone
        # FIXME
        raise Exception("Sorry, the actors parser is currently broken")

    def handle_starttag(self, tag, attrs):
        # <tr id="uiView_SHDevice_16" >
        attrs = dict(attrs)
        if tag == "tr" and 'id' in attrs:
            self.device_id = int(attrs['id'][len('uiView_SHDevice_'):])

        # <td class="c2"><nobr><span title="...">...</span></nobr></td>
        if tag == "td" and attrs.get('class', None) == 'c2':
            self.capture = 'name'
        # <td class="c3"><nobr><span title="...">...</span></nobr></td>
        if tag == "td" and attrs.get('class', None) == 'c3':
            self.capture = 'ain'

    def handle_data(self, data):
        if self.capture == "name":
            self.name = data.strip()
            self.capture = None
        if self.capture == "ain":
            ain = data.strip().replace(' ', '')
            self.actors.append(DeviceInfo(ain, self.device_id, self.name))

            self.capture = None
            self.device_id = None
            self.name = None
