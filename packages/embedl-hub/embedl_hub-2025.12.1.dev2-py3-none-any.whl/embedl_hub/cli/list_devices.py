# Copyright (C) 2025 Embedl AB
"""
embedl-hub list-devices - List all available target devices for the commands
`compile`, `quantize` and `benchmark`.
"""

import typer

list_devices_cli = typer.Typer(
    name="list-devices",
    help="List devices commands (default subcommand: 'embedl').",
    invoke_without_command=True,
)


@list_devices_cli.callback(invoke_without_command=True)
def list_devices_command(ctx: typer.Context):
    """
    List all available target devices.

    A device name is used as input to the `--device` option
    in the commands `compile`, `quantize` and `benchmark`.

    Device lists are available from different providers:
    - `embedl`: Devices from Embedl Cloud (default).
    - `qai-hub`: Devices from Qualcomm AI Hub.
    """
    # pylint: disable=import-outside-toplevel
    from embedl_hub.cli.utils import assert_api_config
    from embedl_hub.core.context import require_initialized_ctx
    # pylint: enable=import-outside-toplevel

    assert_api_config()
    require_initialized_ctx(ctx.obj["config"])

    if ctx.invoked_subcommand is None:
        ctx.invoke(embedl_list_devices_command)


@list_devices_cli.command("embedl")
def embedl_list_devices_command():
    """
    List all available target devices from Embedl Cloud.
    """
    # pylint: disable=import-outside-toplevel
    from embedl_hub.core.hardware.embedl import print_device_table
    # pylint: enable=import-outside-toplevel

    print_device_table()


@list_devices_cli.command("qai-hub")
def qai_hub_list_devices_command():
    """
    List all available target devices from Qualcomm AI Hub.
    """
    # pylint: disable=import-outside-toplevel
    from embedl_hub.core.hardware.qai_hub import print_device_table
    # pylint: enable=import-outside-toplevel

    print_device_table()
