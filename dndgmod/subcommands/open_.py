import os
from typing import Annotated

import typer

def open_(
        ctx: typer.Context,
        slug: Annotated[str, typer.Option("--slug", "-s", help="The slug of the mod to open",
                                          prompt=True)],
):
    """Open the directory of a mod in File Explorer."""
    logger = ctx.obj["logger"]
    mod_directory = ctx.obj["data_directory"] / "mods" / slug

    os.startfile(mod_directory)  # TODO: This only works on Windows
    logger.debug(f"Ran os.startfile on {mod_directory}")
