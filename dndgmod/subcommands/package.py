from typing import Annotated
from tkinter import Tk, filedialog
from zipfile import ZipFile

import typer
import os
import subprocess


def package(
        ctx: typer.Context,
        slug: Annotated[str, typer.Option("--slug", "-s", help="The slug of the mod to package",
                                          prompt=True)],
):
    mod_directory = ctx.obj["data_directory"] / "mods" / slug
    logger = ctx.obj["logger"]

    if not os.path.exists(mod_directory):
        raise FileNotFoundError(f"Directory {mod_directory} does not exist!")

    Tk().withdraw()
    logger.info("Opening a file dialog, select where you want to save your packaged mod to.")
    dndg_file_path = filedialog.asksaveasfilename(title="Save Packaged DnDGMod Mod To...",
                                                  filetypes=[("Packaged DnDGMod Mod", ".dndg.zip")],
                                                  defaultextension=".dndg.zip",
                                                  initialfile=f"{slug}")
    with ZipFile(dndg_file_path, "w") as archive:
        for file_path in mod_directory.rglob("*"):
            archive.write(file_path, arcname=(relative_path := file_path.relative_to(mod_directory)))
            logger.info(f"Packaging {relative_path}...")

    subprocess.Popen(f'explorer /select,"{dndg_file_path.replace('/', '\\')}"')
    logger.info("Packaging successful!")
