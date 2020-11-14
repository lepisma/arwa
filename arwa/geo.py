import IP2Location


class GeoLocator:
    """
    Simple IP address geolocator.
    """

    def __init__(self, ip2location_bin: str):
        self.ip2l = IP2Location.IP2Location()
        self.ip2l.open(ip2location_bin)

    def lookup(self, ip: str):
        return self.ip2l.get_all(ip)
