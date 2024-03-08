import os
from typing import Annotated, Optional

import typer

def open_(
        ctx: typer.Context,
        slug: Annotated[Optional[str], typer.Option("--slug", "-s",
                                                    help="The slug of the mod to open")] = None,
):
    """
    Open the DnDGMod mod directory or a subdirectory in File Explorer.

    If --slug/-s is not provided, this will open the directory that mods are stored in.
    If --slug/-s is provided, this will open the directory of that mod.
    """
    logger = ctx.obj["logger"]
    if slug:
        directory = ctx.obj["data_directory"] / "mods" / slug
    else:
        directory = ctx.obj["data_directory"] / "mods"

    os.startfile(directory)  # TODO: This only works on Windows
    logger.debug(f"Ran os.startfile on {directory}")
