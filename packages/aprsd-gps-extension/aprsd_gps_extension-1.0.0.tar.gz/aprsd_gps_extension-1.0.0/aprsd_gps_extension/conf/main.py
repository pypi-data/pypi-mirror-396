from oslo_config import cfg

extension_group = cfg.OptGroup(
    name="aprsd_gps_extension",
    title="APRSD gps extension settings",
)

extension_opts = [
    cfg.BoolOpt(
        "enabled",
        default=True,
        help="Enable the extension?",
    ),
    cfg.StrOpt(
        "gpsd_host",
        default="localhost",
        help="GPSD host to connect to. Ensure gpsd is running and listening on this host.",
    ),
    cfg.IntOpt(
        "gpsd_port",
        default=2947,
        help="GPSD port to connect to",
    ),
    cfg.IntOpt(
        "polling_interval",
        default=2,
        help="Polling interval in seconds to get the GPS data",
    ),
    cfg.BoolOpt(
        "debug",
        default=False,
        help="Enable debug logging",
    ),
    cfg.StrOpt(
        "beacon_type",
        choices=["none", "interval", "smart"],
        default="none",
        help="The type of beaconing to use. 'none' will not send any beacons, but will fetch the GPS data from gpsd. "
        "'interval' will send a beacon every CONF.beacon_interval seconds. "
        "'smart' will send a beacon when the device has moved a certain distance or time since the last beacon was sent.",
    ),
    cfg.IntOpt(
        "beacon_interval",
        default=1800,
        help="The number of seconds between beacon packets.",
    ),
    cfg.IntOpt(
        "smart_beacon_distance_threshold",
        default=50,
        help="The distance in meters that the device must move before sending a beacon packet,"
        "when smart beaconing is enabled.",
    ),
    cfg.IntOpt(
        "smart_beacon_time_window",
        default=60,
        help="The time window in seconds that the device must be at the same position before sending a beacon packet, when smart beaconing is enabled.",
    ),
]

ALL_OPTS = extension_opts


def register_opts(cfg):
    cfg.register_group(extension_group)
    cfg.register_opts(ALL_OPTS, group=extension_group)


def list_opts():
    return {
        extension_group.name: extension_opts,
    }
