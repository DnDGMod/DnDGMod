from zipfile import ZipFile
from pathlib import Path
import shutil
import logging

from ..exceptions import InvalidDnDGModZIPPackageFormatException
from ..util import files


def unpackage(zip_file_path: Path, logger=None):
    if not logger:
        logger = logging
    logger.info("DnDGMod by TotallyNotSeth\n\n")
    data_directory = files.get_appdata_directory()
    logger.debug(f"AppData directory: {data_directory}")
    mod_directory = data_directory / "mods" / zip_file_path.name.rstrip(".zip")
    logger.info(f"Source ZIP: {zip_file_path}")
    logger.info(f"Destination directory: {mod_directory}")
    with ZipFile(zip_file_path, "r") as archive:
        logger.info("Extracting...")
        archive.extractall(mod_directory)
    if not (mod_directory / "mod.yaml").exists():
        if ((submod_directory := mod_directory / mod_directory.stem) / "mod.yaml").exists():
            shutil.copytree(submod_directory, mod_directory, dirs_exist_ok=True)
            shutil.rmtree(submod_directory)
            logger.info("Mod loaded!")
        else:
            shutil.rmtree(mod_directory)
            logger.error(f"{zip_file_path} Has An Invalid DnDGMod ZIP Package Format")
    else:
        logger.info("Mod loaded!")
