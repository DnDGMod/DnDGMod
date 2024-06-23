from ..util.progress import ProgressTracker

from typing import Annotated
from urllib.request import urlretrieve
from zipfile import ZipFile

import typer


def init(
        ctx: typer.Context,
):
    """Initialize DnDGMod and install _dependencies.

    This will automatically download Godot 3.5.3 and GDRE Tools 0.6.2 to the DnDGMod AppData directory."""
    logger = ctx.obj["logger"]

    logger.debug("Ensuring AppData directory exists...")
    mods_directory = ctx.obj["data_directory"] / "mods"
    if not mods_directory.exists():
        mods_directory.mkdir(parents=True)
        logger.info("Created AppData directory")
