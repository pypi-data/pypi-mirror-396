import logging
import signal
import sys
import time

import aprsd
import click
from aprsd import cli_helper
from gpsdclient import GPSDClient
from oslo_config import cfg
from rich.console import Console

import aprsd_gps_extension

# Import the extension's configuration options
from aprsd_gps_extension import (  # noqa
    cmds,
    conf,  # noqa
    utils,
)
from aprsd_gps_extension.gps_processor import SmartBeaconProcessor
from aprsd_gps_extension.stats import GPSStats

CONF = cfg.CONF
LOG = logging.getLogger("APRSD")


def signal_handler(sig, frame):
    print("signal_handler: called")
    # APRSD based threads are automatically added
    # to the APRSDThreadList when started.
    # This will tell them all to stop.
    sys.exit(0)


@cmds.gps.command()
@cli_helper.add_options(cli_helper.common_options)
@click.option(
    "--host",
    default=None,
    help="GPS daemon host. Defaults to CONF.aprsd_gps_extension.gpsd_host",
)
@click.option(
    "--port",
    default=None,
    help="GPS daemon port. Defaults to CONF.aprsd_gps_extension.gpsd_port",
    type=int,
)
@click.option(
    "--stats",
    is_flag=True,
    default=False,
    help="Show the GPS stats.",
)
@click.pass_context
@cli_helper.process_standard_options
def show(ctx, host, port, stats):
    """Show the GPS data from the gpsdclient."""

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    LOG.info(f"APRSD version: {aprsd.__version__}")
    level, msg = utils._check_version()
    if level:
        LOG.warning(msg)
    else:
        LOG.info(msg)
    version = aprsd_gps_extension.__version__
    LOG.info(f"APRSD gps show started version: {version}")

    # Dump all the config options now.
    CONF.log_opt_values(LOG, logging.DEBUG)
    console = Console()

    # Now add your code here to start your extension.
    # You know that you have a client configured and connected
    # Create your threads, and start them here.

    if not CONF.aprsd_gps_extension.enabled:
        console.print("[red]GPS extension is not enabled, exiting[/red]")
        sys.exit(-1)

    # Make sure we have a valid host and port
    if not host:
        host = CONF.aprsd_gps_extension.gpsd_host
    if not port:
        port = CONF.aprsd_gps_extension.gpsd_port
    if not host or not port:
        console.print("[red]GPS host and port are not set, exiting[/red]")
        sys.exit(-1)

    distance_threshold = CONF.aprsd_gps_extension.smart_beacon_distance_threshold
    time_window = CONF.aprsd_gps_extension.smart_beacon_time_window
    beacon_processor = SmartBeaconProcessor(
        distance_threshold_feet=CONF.aprsd_gps_extension.smart_beacon_distance_threshold,
        time_window_minutes=CONF.aprsd_gps_extension.smart_beacon_time_window,
    )

    # now lets create the gpsdclient object that
    try:
        client = GPSDClient(host=host, port=port)
    except Exception as e:
        console.print(f"[red]Error connecting to GPS daemon: {e}[/red]")
        return

    with console.status("Connecting to GPS daemon") as status:
        while True:
            time.sleep(5)

            try:
                # Collect the latest TPV and SKY messages from the stream
                tpv_data = None
                sky_data = None

                status.update("Polling GPS daemon")
                for message in client.dict_stream(convert_datetime=True):
                    console.print(f"[green]Message:[/green] {message}")
                    # process the message
                    GPSStats().parse_message(message)

                    msg_class = message.get("class")
                    match msg_class:
                        case "TPV":
                            tpv_data = message
                        case "SKY":
                            sky_data = message
                        case _:
                            pass

                    # Once we have TPV data, process and break
                    if tpv_data:
                        break

                if not tpv_data:
                    console.print("[yellow]No GPS data available (no fix)[/yellow]")
                    continue

                if stats:
                    console.print(f"[green]GPS(TPV) stats:[/green] {tpv_data}")
                    console.print(f"[green]GPS(SKY) stats:[/green] {sky_data}")

                # Check if we should beacon based on smart beaconing logic
                should_beacon, distance_feet = beacon_processor.should_beacon(tpv_data)

                if not should_beacon:
                    # Position hasn't changed enough or time window hasn't passed
                    if distance_feet is not None:
                        status.update(
                            f"[dim]Waiting for position change > {distance_threshold}ft within {time_window}min... (last: {distance_feet:.1f}ft)[/dim]"
                        )
                    else:
                        status.update("[dim]Waiting for valid position data...[/dim]")
                    continue

                # Display GPS information (only if beaconing)
                try:
                    # mode = tpv_data.get("mode", "N/A")
                    # console.print(f"[green]Mode:[/green] {mode}")

                    timestamp = tpv_data.get("time", "N/A")
                    # console.print(f"[green]Timestamp:[/green] {timestamp}")

                    # Satellite data from SKY message
                    if sky_data:
                        try:
                            satellites = sky_data.get("satellites", [])
                            used_count = sum(
                                1 for sat in satellites if sat.get("used", False)
                            )
                            total_count = len(satellites)
                            console.print(
                                f"[green]Satellites (used/total):[/green] {used_count} / {total_count}"
                            )
                        except (AttributeError, KeyError):
                            console.print(
                                "[yellow]Satellite data not available[/yellow]"
                            )

                    # Position data from TPV message
                    try:
                        lat = tpv_data.get("lat")
                        lon = tpv_data.get("lon")
                        alt = tpv_data.get("alt", "N/A")

                        if lat is not None and lon is not None:
                            if distance_feet is not None:
                                status.update(
                                    f"[bold green]Position:[/bold green] {lat}, {lon}, {alt}m  --  {timestamp}  [cyan](moved {distance_feet:.1f}ft)[/cyan]"
                                )
                            else:
                                status.update(
                                    f"[bold green]Position:[/bold green] {lat}, {lon}, {alt}m  --  {timestamp}"
                                )
                        else:
                            console.print(
                                "[yellow]Position data not available (no fix)[/yellow]"
                            )
                    except (AttributeError, KeyError):
                        console.print("[yellow]Position data not available[/yellow]")

                except AttributeError as e:
                    console.print(f"[yellow]Some GPS data unavailable: {e}[/yellow]")

            except KeyboardInterrupt:
                console.print("\n[yellow]Interrupted by user[/yellow]")
                break
            except Exception as e:
                console.print(f"[red]Error polling GPS daemon: {e}[/red]")
                continue
