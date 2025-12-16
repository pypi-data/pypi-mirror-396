import logging

from oslo_config import cfg

CONF = cfg.CONF
LOG = logging.getLogger("APRSD")


class GPSStats:
    """The GPSStats class is used to collect stats from the GPS extension."""

    _key_lookup = {
        "time": "time",
        "latitude": "lat",
        "longitude": "lon",
        "altitude": "alt",
        "altHAE": "altHAE",
        "altMSL": "altMSL",
        "climb": "climb",
        "mode": "mode",
        "track": "track",
        "speed": "speed",
        "magvar": "magvar",
        "devices": "devices",
    }
    data = {
        "fix": False,
        "time": None,
        "latitude": None,
        "longitude": None,
        "altitude": None,
        "altHAE": None,
        "altMSL": None,
        "climb": None,
        "mode": None,
        "magnetic_variation": None,
        "track": None,
        "speed": None,
        "heading": None,
        "satellites": None,
        "version": None,
    }
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GPSStats, cls).__new__(cls)
        return cls._instance

    def parse_message(self, message: dict):
        """parse the raw message from the gpsd client and update the stats."""
        # LOG.debug(message)
        match message.get("class"):
            case "TPV":
                # LOG.debug(f"TPV message: {message}")
                if message.get("lat") is not None and message.get("lon") is not None:
                    fix = True
                else:
                    fix = False

                self.data["fix"] = fix

                for key, value in self._key_lookup.items():
                    self.data[key] = message.get(value)
            case "SKY":
                # LOG.debug(f"SKY message: {message}")
                self.data["satellites"] = message.get("satellites")
            case "VERSION":
                # LOG.debug(f"VERSION message: {message}")
                self.data["version"] = message.get("version")
            case "DEVICES":
                # LOG.debug(f"DEVICES message: {message}")
                self.data["devices"] = message.get("devices")
            case "PPS":
                # LOG.debug(f"PPS message: {message}")
                pass
            case "WATCH":
                # LOG.debug(f"WATCH message: {message}")
                pass
            case "ERROR":
                # LOG.debug(f"ERROR message: {message}")
                self.data["fix"] = False
                for key, value in self._key_lookup.items():
                    self.data[key] = None
            case _:
                # LOG.warning(f"Unknown message class: {message.get('class')}")
                return

    def stats(self, serializable=False):
        if serializable:
            if self.data["time"]:
                self.data["time"] = str(self.data["time"])
        return self.data
