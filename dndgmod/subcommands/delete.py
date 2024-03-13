import os
import shutil
from typing import Annotated

import typer
import yaml

def delete(
        ctx: typer.Context,
        slug: Annotated[str, typer.Option("--slug", "-s", help="The slug of the mod to delete",
                                          prompt=True, confirmation_prompt=True)],
):
    """Delete an existing mod."""
    mod_directory = ctx.obj["data_directory"] / "mods" / slug
    logger = ctx.obj["logger"]

    if not os.path.exists(mod_directory):
        raise FileNotFoundError(f"Directory {mod_directory} does not exist!")

    with open(mod_directory / "mod.yaml") as f:
        data = yaml.safe_load(f)
        name = data["name"]

    logger.info(f"Deleting mod {name} at {mod_directory}...")
    shutil.rmtree(mod_directory)
    logger.info(f"Successfully deleted mod {name} at {mod_directory}")
