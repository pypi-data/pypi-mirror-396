import logging
import time

from aprsd import threads as aprsd_threads
from aprsd.packets import core
from aprsd.stats import collector
from aprsd.threads import tx as aprsd_tx
from gpsdclient import GPSDClient
from oslo_config import cfg

from aprsd_gps_extension.conf import main  # noqa: F401
from aprsd_gps_extension.gps_processor import SmartBeaconProcessor
from aprsd_gps_extension.stats import GPSStats

CONF = cfg.CONF
LOG = logging.getLogger("APRSD")


class GPSBeaconThread(aprsd_threads.APRSDThread):
    """Thread the reads the GPS data from gpsdclient and sends a beacon packet
    based on either smart beaconing or regular beaconing.

    regular beaconing is when the beacon is sent every CONF.beacon_interval seconds.
    smart beaconing is when the beacon is sent only if the device has moved a certain
    distance or time since the last beacon was sent.
    """

    def __init__(self, notify_queue):
        super().__init__("GPSClientThread")
        self.client = None
        self.setup()
        # Now setup the initial timer
        self.last_beacon_time = time.time()
        self.notify_queue = notify_queue

    def setup(self):
        LOG.info("GPSClientThread setup")
        if not CONF.enable_beacon:
            LOG.error("Beaconing is disabled, stopping thread.")
            LOG.error(
                "Enable beaconing in the config file with CONF.enable_beacon = True."
            )
            self.stop()
            return False

        if not CONF.aprsd_gps_extension.gpsd_host:
            LOG.error("GPSD host not set")
            return

        try:
            LOG.info(
                f"Connecting to GPS daemon: {CONF.aprsd_gps_extension.gpsd_host}:{CONF.aprsd_gps_extension.gpsd_port}"
            )
            self.client = GPSDClient(
                host=CONF.aprsd_gps_extension.gpsd_host,
                port=CONF.aprsd_gps_extension.gpsd_port,
            )
            LOG.info("Connected to GPS daemon")
        except Exception as e:
            LOG.error(f"Error connecting to GPS daemon: {e}")
            return

        stats_collector = collector.Collector()
        stats_collector.register_producer(GPSStats)
        self.beacon_interval = CONF.beacon_interval
        self.polling_interval = CONF.aprsd_gps_extension.polling_interval
        self.beacon_type = CONF.aprsd_gps_extension.beacon_type
        self.smart_beacon_distance_threshold = (
            CONF.aprsd_gps_extension.smart_beacon_distance_threshold
        )
        self.smart_beacon_time_window = (
            CONF.aprsd_gps_extension.smart_beacon_time_window
        )
        self.beacon_processor = SmartBeaconProcessor(
            distance_threshold_feet=CONF.aprsd_gps_extension.smart_beacon_distance_threshold,
            time_window_minutes=CONF.aprsd_gps_extension.smart_beacon_time_window,
        )

    def _debug(self, message):
        if CONF.aprsd_gps_extension.debug:
            LOG.debug(f"GPS: {message}")

    def update_settings(self, message):
        self.beacon_interval = message.get("beacon_interval")
        self.beacon_type = message.get("beacon_type")
        self.smart_beacon_distance_threshold = message.get(
            "smart_beacon_distance_threshold"
        )
        self.smart_beacon_time_window = message.get("smart_beacon_time_window")
        # rebuild the SmartBeaconProcessor
        self.beacon_processor = SmartBeaconProcessor(
            distance_threshold_feet=self.smart_beacon_distance_threshold,
            time_window_minutes=self.smart_beacon_time_window,
        )

    def send_beacon(self, tpv_data, sky_data):
        LOG.info("Sending beacon")
        pkt = core.BeaconPacket(
            from_call=CONF.callsign,
            to_call="APRS",
            latitude=tpv_data.get("lat"),
            longitude=tpv_data.get("lon"),
            comment="APRSD GPS Beacon",
            symbol=CONF.beacon_symbol,
        )
        aprsd_tx.send(pkt, direct=True)
        self.last_beacon_time = time.time()
        self.notify_queue.put({"message": "beacon sent"})

    def get_gps_settings(self):
        LOG.info("Getting GPS settings")
        self.notify_queue.put(
            {"message": "gps_settings", "settings": self.get_settings()}
        )

    def get_settings(self):
        return {
            "beacon_type": self.beacon_type,
            "beacon_interval": self.beacon_interval,
            "smart_beacon_distance_threshold": self.smart_beacon_distance_threshold,
            "smart_beacon_time_window": self.smart_beacon_time_window,
        }

    def loop(self):
        # First check if the notify queue has a message
        if not self.notify_queue.empty():
            message = self.notify_queue.get_nowait()
            LOG.info(f"Notify queue message: {message}")
            match message.get("message"):
                case "get_gps_settings":
                    self.get_gps_settings()
                case "beaconing_settings_changed":
                    self.update_settings(message)
                case "beacon sent":
                    # put it back on the queue
                    self.notify_queue.put(message)
                case _:
                    LOG.warning(f"Unknown message: {message}")
                    self.notify_queue.put(message)

        if self.loop_count % CONF.aprsd_gps_extension.polling_interval == 0:
            # Collect the latest TPV and SKY messages from the stream
            tpv_data = None
            sky_data = None

            LOG.info("Polling GPS daemon")
            try:
                # Read messages to get the latest TPV and SKY
                self._debug("Reading messages from GPS daemon")
                for message in self.client.dict_stream(convert_datetime=True):
                    msg_class = message.get("class")
                    self._debug(f"Message class: {msg_class}")
                    # process the message
                    GPSStats().parse_message(message)

                    if msg_class == "TPV":
                        tpv_data = message
                    elif msg_class == "SKY":
                        sky_data = message
                    self._debug(f"TPV data: {tpv_data}")
                    self._debug(f"SKY data: {sky_data}")

                    # Once we have TPV data, process and break
                    if tpv_data:
                        break

                if not tpv_data:
                    LOG.warning("No GPS data available (no fix)")
                    time.sleep(1)
                    return True

                # Check if we should beacon based on smart beaconing logic
                if self.beacon_type == "smart":
                    should_beacon, distance_feet = self.beacon_processor.should_beacon(
                        tpv_data
                    )
                    if should_beacon:
                        LOG.info("Sending beacon, enough movement or time has passed")
                        self.send_beacon(tpv_data, sky_data)
                    else:
                        LOG.info(
                            "Not sending beacon, not enough movement or time has passed"
                        )
                        time.sleep(1)
                        return True
                elif self.beacon_type == "interval":
                    # Now only beacon if the time interval from CONF.beacon_interval has passed
                    if time.time() - self.last_beacon_time < self.beacon_interval:
                        LOG.info("Not sending beacon, time interval has not passed")
                        time.sleep(1)
                        return True
                    else:
                        self.send_beacon(tpv_data, sky_data)
                else:
                    LOG.info("Not sending beacon, beacon type is not set")
                    time.sleep(1)
                    return True

            except Exception as e:
                LOG.error(f"Error polling GPS daemon: {e}")
                GPSStats().parse_message({"class": "ERROR"})
                time.sleep(1)
                return True

        time.sleep(1)
        return True
