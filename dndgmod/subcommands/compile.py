import shutil

from ..util import files
from ..util.patch import patch_dndg

import subprocess
import logging


def compile_dndg(logger: logging.Logger = None, clear_save_game: bool = True, debug: bool = False,
                 launch_dndg: bool = True):
    """Compile modded Dungeons & Degenerate Gamblers."""
    if not logger:
        logger = logging
    logger.info("DnDGMod by TotallyNotSeth\n\n")
    appdata_directory = files.get_appdata_directory(logger=logger)
    logger.debug(f"AppData Directory: {appdata_directory}")
    patch_dndg(logger=logger)
    if clear_save_game and (save_location := files.get_godot_data_directory() / "app_userdata" /
                            "Dungeons & Degenerate Gamblers" / "0").exists():
        logger.info("Clearing modded save data")
        shutil.rmtree(save_location)

    pck_path = files.get_dndg_pck_path()
    logger.debug(f"D&DG .pck Path: {pck_path}")
    exe_path = pck_path.parent / "DnDG_64.exe"

    logger.info("Compiling D&DG with Godot (this may take a moment)")
    process = subprocess.Popen([appdata_directory / "dependencies" / "godot.exe", "--no-window", "--path",
                                appdata_directory / "modified_src", "--export" + ("-debug" * debug), "dndgmod",
                                exe_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    with process.stdout:
        for line in iter(process.stdout.readline, b''):  # b'\n'-separated lines
            logger.debug(line.decode("utf-8"))
    logger.info("\nCompile Complete")
    if launch_dndg:
        logger.info("\nLaunching D&DG")
        process = subprocess.Popen([exe_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        with process.stdout:
            for line in iter(process.stdout.readline, b''):  # b'\n'-separated lines
                logger.debug(line.decode("utf-8"))
