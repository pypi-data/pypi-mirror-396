# Copyright (C) 2025 Embedl AB

"""
embedl-hub auth - authenticate with your API key
"""

from __future__ import annotations

import typer

auth_cli = typer.Typer(help="Initialise / show project & experiment context")


@auth_cli.command("auth")
def auth_command(
    ctx: typer.Context,
    api_key: str = typer.Option(
        ...,
        "--api-key",
        help="Set or update API key. Generate one at https://hub.embedl.com/profile.",
        show_default=False,
    ),
):
    """
    Store the API key for embedl-hub CLI.

    Examples
    --------
    Configure the API key:
        $ embedl-hub auth --api-key <your-key>
    """

    # pylint: disable=import-outside-toplevel
    from embedl_hub.core.context import write_ctx_config
    from embedl_hub.core.hub_logging import console
    # pylint: enable=import-outside-toplevel

    ctx.obj["config"]["api_key"] = api_key
    write_ctx_config(ctx.obj["config"])

    console.print("[green]✓ Stored API key[/]")
