from .._util.slug import generate_slug

import os
from typing import Annotated

import click
import typer
import yaml

def slug_factory():
    ctx = click.get_current_context()
    name = ctx.params["name"]
    return generate_slug(name)

def create(
        ctx: typer.Context,
        name: Annotated[str, typer.Option("--name", "-n", help="The name of the mod",
                                          prompt="Mod Name")],
        creator: Annotated[str, typer.Option("--creator", "-c", help="The creator of the mod",
                                             prompt=True)],
        slug: Annotated[str, typer.Option("--slug", "-s",
                                          help="The slug (terminal-friendly name) of the mod",
                                          default_factory=slug_factory, rich_help_panel="Advanced Options")],
        description: Annotated[str, typer.Option("--description", "-d",
                                                 help="The description of the mod")] = "A DnDG Mod",
        version: Annotated[str, typer.Option("--version", "-v",
                                             help="The version of the mod")] = "0.1.0",
        export_cards: Annotated[bool, typer.Option(help="Generate files for creating custom cards.",
                                                   rich_help_panel="Advanced Options")] = True,
        export_encounters: Annotated[bool, typer.Option(help="Generate files for creating custom encounters.",
                                                        rich_help_panel="Advanced Options")] = False,
        open_directory: Annotated[bool, typer.Option(help="Open the mod's directory in File Explorer after mod "
                                                          "creation.", rich_help_panel="Advanced Options")] = True,
):
    """Create a blank mod."""
    mod_directory = ctx.obj["data_directory"] / "mods" / slug
    logger = ctx.obj["logger"]
    logger.info(f"Creating '{name}' at {mod_directory}...")

    if mod_directory.exists():
        raise FileExistsError(f"{mod_directory} exists, a new mod cannot be created there.")
    mod_directory.mkdir()
    logger.debug(f"Created mod {name} directory at {mod_directory}")

    with open(mod_directory / "mod.yaml", "w") as f:
        exports = []
        if export_cards:
            exports.append("cards")
        if export_encounters:
            exports.append("encounters")
        data = {
            "name": name,
            "description": description,
            "creator": creator,
            "version": version,
            "exports": exports,
        }
        yaml.safe_dump(data, f, sort_keys=False)
    logger.debug(f"Created mod {name} properties file at {mod_directory / 'mod.yaml'}")

    os.mkdir(mod_directory / "res")
    logger.debug(f"Created mod {name} resources directory at {mod_directory / 'res'}")
    os.mkdir(mod_directory / "src")
    logger.debug(f"Created mod {name} source code directory at {mod_directory / 'src'}")

    with open(mod_directory / "cards.yaml", "w") as f:
        f.write("# Add your cards here!")
    logger.debug(f"Created mod {name} cards file at {mod_directory / 'cards.yaml'}")
    with open(mod_directory / "encounters.yaml", "w") as f:
        f.write("# Add your encounters here!")
    logger.debug(f"Created mod {name} encounters file at {mod_directory / 'encounters.yaml'}")

    logger.info(f"Mod {name} created at {mod_directory}")
    if open_directory:
        os.startfile(mod_directory)
