import click

from aprsd.cli_helper import AliasedGroup
from aprsd.main import cli


@cli.group(cls=AliasedGroup, aliases=['gps'], help="APRSD GPSD Extension to provide active GPS")
@click.pass_context
def gps(ctx):
    pass
