# Copyright (C) 2025 Embedl AB

"""
Functionality for handling the Embedl Cloud communication and device management.
"""

from rich.table import Table

from embedl_hub.core.hub_logging import console
from embedl_hub.tracking import get_devices


def print_device_table():
    """Print a table of available devices on the Embedl Cloud."""
    devices = get_devices()

    table = Table(title="Embedl Hub devices")
    table.add_column("Name", style="cyan")
    table.add_column("Vendor")
    table.add_column("Platform")
    table.add_column("OS")
    table.add_column("Type")

    for device in devices:
        table.add_row(
            device.name,
            device.vendor,
            device.platform,
            device.os,
            device.type,
        )

    console.print(table)
