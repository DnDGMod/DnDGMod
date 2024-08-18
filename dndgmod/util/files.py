import logging

import appdirs
import wget
import shutil

import re
from pathlib import Path
import winreg
import os
from zipfile import ZipFile

from ..exceptions import DnDGNotFoundException


def get_dndg_pck_path() -> Path:
    """Locates where D&DG is installed.

    Scans for Steam's libraryfolders.vdf, parses it to find the locations of all Steam libraries, then scans each
    library until Dungeons & Degenerate Gamblers is found and finally returns the path to DnDG_64.pck.

    Returns:
        The path to DnDG_64.pck
    """
    if not (library_folders := Path("C:/Program Files (x86)/Steam/steamapps/libraryfolders.vdf")).exists():
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\Wow6432Node\\Valve\\Steam")
        library_folders = Path(winreg.QueryValueEx(key, "InstallPath")[0]) / "steamapps" / "libraryfolders.vdf"
    with open(library_folders) as f:
        matches = re.finditer("\"path\"\t\t\"(.*?)\"", f.read())
    for match in matches:
        library = (Path(match.groups()[0]) / "steamapps" / "common").resolve(strict=True)
        dndg_path = library / "Dungeons & Degenerate Gamblers" / "DnDG_64.pck"
        print(dndg_path)
        if dndg_path.exists():
            return dndg_path
    else:
        raise DnDGNotFoundException("Dungeons & Degenerate Gamblers could not be found. "
                                    "Make sure it's installed via Steam!")


def get_godot_data_directory() -> Path:
    return Path(os.getenv("APPDATA")) / "Godot"


def get_appdata_directory(logger: logging.Logger = None) -> Path:
    if not logger:
        logger = logging

    appdata_directory = Path(appdirs.user_data_dir("DnDGMod", "TotallyNotSeth"))
    if not appdata_directory.exists():
        appdata_directory.mkdir(parents=True)
        (appdata_directory / "mods").mkdir()
        (appdata_directory / "src").mkdir()
    dependencies_directory = appdata_directory / "dependencies"
    if not (appdata_directory / "prefs.yaml").exists():
        logger.info("Upgrading to DnDGMod Lite Filesystem...")
        shutil.rmtree(appdata_directory / "dependencies", ignore_errors=True)
        shutil.rmtree(appdata_directory / "modified_src", ignore_errors=True)
        shutil.rmtree(appdata_directory / "src", ignore_errors=True)
        (appdata_directory / "DnDG_vanilla.pck").unlink(missing_ok=True)
        (appdata_directory / "DnDG_vanilla.exe").unlink(missing_ok=True)
        with open(appdata_directory / "prefs.yaml", "w") as f:
            f.write("Version: 0.1.0-lite")
        logger.info("Filesystem Upgrade Complete")
    if not dependencies_directory.exists():
        logger.warning("This appears to be your first time running DnDGMod Lite. Please hold while we grab a few "
                       "dependencies.")
        logger.info("Creating dependency destination directory")
        dependencies_directory.mkdir()
        logger.info("Downloading dependencies ZIP from S3 server")
        wget.download("https://dndgmod.s3.us-east-2.amazonaws.com/dndgmod_dependencies.zip",
                      str(dependencies_directory / "dndgmod_dependencies.zip"))
        logger.info("Extracting dependencies ZIP to destination directory")
        with ZipFile(dependencies_directory / "dndgmod_dependencies.zip") as zip_file:
            for file in zip_file.namelist():
                logger.info(f"Extracting {file}")
                zip_file.extract(file, dependencies_directory)
        logger.info("Deleting dependencies ZIP")
        (dependencies_directory / "dndgmod_dependencies.zip").unlink()
        logger.info("Dependency acquisition completed!")
    return appdata_directory


def replace_in_file(file: Path, old: str, new: str):
    """Performs a string replacement within a file.

    Args:
        file: A file to do the replacement on.
        old: The string to find and replace.
        new: The string to replace all instances of the old string with.
    """
    with open(file) as f:
        file_contents = f.read()
    with open(file, "w") as f:
        f.write(file_contents.replace(old, new))
