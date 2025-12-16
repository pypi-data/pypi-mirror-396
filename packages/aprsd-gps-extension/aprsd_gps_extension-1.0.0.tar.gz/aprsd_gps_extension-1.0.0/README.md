APRSD GPSD Extension
====================

[![PyPI](https://img.shields.io/pypi/v/aprsd-gps-extension.svg)](https://pypi.org/project/aprsd-gps-extension/)
[![Status](https://img.shields.io/pypi/status/aprsd-gps-extension.svg)](https://pypi.org/project/aprsd-gps-extension/)
[![Python Version](https://img.shields.io/pypi/pyversions/aprsd-gps-extension)](https://pypi.org/project/aprsd-gps-extension)
[![License](https://img.shields.io/pypi/l/aprsd-gps-extension)](https://opensource.org/licenses/Apache Software License 2.0)

[![Read the documentation at https://aprsd-gps-extension.readthedocs.io/](https://img.shields.io/readthedocs/aprsd-gps-extension/latest.svg?label=Read%20the%20Docs)](https://aprsd-gps-extension.readthedocs.io/)
[![Tests](https://github.com/hemna/aprsd-gps-extension/workflows/Tests/badge.svg)](https://github.com/hemna/aprsd-gps-extension/actions?workflow=Tests)
[![Codecov](https://codecov.io/gh/hemna/aprsd-gps-extension/branch/main/graph/badge.svg)](https://codecov.io/gh/hemna/aprsd-gps-extension)

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

---

> [!WARNING]
> Legal operation of this software requires an amateur radio license and a valid call sign.

> [!NOTE]
> Star this repo to follow our progress! This code is under active development, and contributions are both welcomed and appreciated. See [CONTRIBUTING.md](<https://github.com/craigerl/aprsd/blob/master/CONTRIBUTING.md>) for details.

# Features

-   Connect to GPSD (GPS daemon) to retrieve GPS coordinates
-   Support for local and remote GPSD servers
-   Automatic APRS beaconing based on GPS position
-   Smart beaconing that sends beacons when the device moves a certain distance
-   Interval-based beaconing for regular position updates
-   Real-time GPS data polling and processing

# Requirements

-   `aprsd >= 4.2.4`
-   A running GPSD daemon (either local or remote)
-   GPSD must be accessible via TCP/IP on the configured host and port

# Installation

You can install *APRSD GPSD Extension* via [pip](https://pip.pypa.io/) from [PyPI](https://pypi.org/):

``` console
$ pip install aprsd-gps-extension
```

Or using `uv`:

``` console
$ uv pip install aprsd-gps-extension
```

# Configuration

Before using the GPS extension, you need to configure it in your APRSD configuration file.
Generate a sample configuration file if you haven't already:

``` console
$ aprsd sample-config
```

This will create a configuration file at `~/.config/aprsd/aprsd.conf` (or `aprsd.yml`).

## GPSD Connection Settings

Add the following section to your APRSD configuration file to configure the GPS extension:

``` yaml
[aprsd_gps_extension]
# Enable the GPS extension (default: True)
enabled = True

# GPSD host to connect to (default: localhost)
# For remote GPSD, specify the IP address or hostname
gpsd_host = localhost

# GPSD port to connect to (default: 2947)
gpsd_port = 2947

# Polling interval in seconds to get GPS data (default: 2)
polling_interval = 2

# Enable debug logging (default: False)
debug = False
```

### Connecting to a Remote GPSD Server

To connect to a remote GPSD server, simply set the `gpsd_host` to the IP address or hostname
of the remote server:

``` yaml
[aprsd_gps_extension]
enabled = True
gpsd_host = 192.168.1.100  # Remote GPSD server IP
gpsd_port = 2947            # Default GPSD port
polling_interval = 2
```

**Important**: Ensure that:
1. The remote GPSD server is running and accessible
2. The GPSD port (default 2947) is not blocked by a firewall
3. Your GPS device is connected and providing data to GPSD on the remote server

## Beacon Configuration

The GPS extension supports three beaconing modes:

### No Beaconing (`none`)

The extension will fetch GPS data but won't send any beacons. This is useful if you only
want to track GPS position without broadcasting it.

``` yaml
[aprsd_gps_extension]
beacon_type = none
```

### Interval Beaconing (`interval`)

Sends a beacon at regular intervals regardless of movement.

``` yaml
[aprsd_gps_extension]
beacon_type = interval
beacon_interval = 1800  # Send beacon every 1800 seconds (30 minutes)
```

### Smart Beaconing (`smart`)

Sends beacons only when the device has moved a certain distance or after a time window.
This is more efficient and reduces unnecessary beacons when stationary.

``` yaml
[aprsd_gps_extension]
beacon_type = smart
smart_beacon_distance_threshold = 50   # Send beacon after moving 50 meters
smart_beacon_time_window = 60           # Send beacon if stationary for 60 seconds
```

## Complete Configuration Example

Here's a complete example configuration for connecting to a remote GPSD server with smart beaconing:

``` yaml
[aprsd_gps_extension]
enabled = True
gpsd_host = 192.168.1.100
gpsd_port = 2947
polling_interval = 2
debug = False
beacon_type = smart
beacon_interval = 1800
smart_beacon_distance_threshold = 50
smart_beacon_time_window = 60
```

## Enabling Beaconing

The GPS extension requires that APRSD beaconing is enabled in the main configuration:

``` yaml
[DEFAULT]
enable_beacon = True
beacon_interval = 1800
beacon_symbol = /
```

# Usage

Once installed and configured, the GPS extension will automatically start when you run
`aprsd server` or `aprsd webchat` (if the webchat extension is installed).

The extension will:
1. Connect to the configured GPSD server
2. Poll GPS data at the specified interval
3. Send beacons according to the configured beacon type
4. Provide GPS statistics via the APRSD stats system

You can verify the GPS extension is working by checking the logs for messages like:

```
INFO: Connecting to GPS daemon: 192.168.1.100:2947
INFO: Connected to GPS daemon
INFO: GPS fix acquired
```

For more details, see the [Command-line Reference](https://aprsd-gps-extension.readthedocs.io/en/latest/usage.html).

# Contributing

Contributions are very welcome. To learn more, see the [Contributor
Guide](CONTRIBUTING.rst).

# License

Distributed under the terms of the
[Apache Software License 2.0 license](https://opensource.org/licenses/Apache Software License 2.0), *APRSD GPSD Extension* is free and open source software.

# Issues

If you encounter any problems, please [file an issue](https://github.com/hemna/aprsd-gps-extension/issues)
along with a detailed description.

# Credits

This project was generated from [@hemna](https://github.com/hemna)\'s
[APRSD Extension Python Cookiecutter]() template.
