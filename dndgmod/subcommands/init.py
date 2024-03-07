from .._util.progress import ProgressTracker

from typing import Annotated
from urllib.request import urlretrieve
from zipfile import ZipFile

import typer

def init(
        ctx: typer.Context,
        godot_url: Annotated[str, typer.Option(
            help="The URL to download a ZIP file containing the Windows version of Godot 3.5.3 from"
            # TODO: Linux users don't like being alienated (I should know, I am one)
        )] = "https://github.com/godotengine/godot/releases/download/3.5.3-stable/Godot_v3.5.3-stable_win64.exe.zip",
        gdre_url: Annotated[str, typer.Option(
            help="The URL to download a ZIP file containing the Windows version of GDRE Tools from"
        )] = "https://github.com/bruvzg/gdsdecomp/releases/download/v0.6.2/GDRE_tools-v0.6.2-windows.zip",
):
    logger = ctx.obj["logger"]
    status_tracker = ProgressTracker(logger)

    logger.debug("Ensuring AppData directory exists...")
    mods_directory = ctx.obj["data_directory"] / "mods"
    if not mods_directory.exists():
        mods_directory.mkdir(parents=True)
        logger.info("Created AppData directory")

    logger.debug("Ensuring dependencies directory exists...")
    dependencies_directory = ctx.obj["data_directory"] / "dependencies"
    if not dependencies_directory.exists():
        dependencies_directory.mkdir(parents=True)
        logger.debug("Created dependencies directory")

    # TODO: We might be able to unzip the download while it downloads... but that sounds like WORK
    logger.info("Retrieving Godot from the Internet...")
    godot_zip_path = dependencies_directory / "godot.zip"
    urlretrieve(godot_url, godot_zip_path, status_tracker.print_progress)
    logger.debug("Extracting Godot to the AppData directory...")
    with ZipFile(godot_zip_path, "r") as godot_zip:
        godot_zip.extractall(dependencies_directory)
    logger.debug("Cleaning up Godot ZIP file...")
    godot_zip_path.unlink()

    logger.info("Retrieving GDRE Tools from the Internet...")
    status_tracker.reset()
    gdre_zip_path = dependencies_directory / "gdre_tools.zip"
    urlretrieve(gdre_url, gdre_zip_path, status_tracker.print_progress)
    logger.debug("Extracting GDRE Tools to the AppData directory...")
    with ZipFile(gdre_zip_path, "r") as gdre_zip:
        gdre_zip.extractall(dependencies_directory)
    logger.debug("Cleaning up GDRE Tools ZIP file...")
    gdre_zip_path.unlink()
