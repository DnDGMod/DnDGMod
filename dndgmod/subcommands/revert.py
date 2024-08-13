import logging

from ..util import files

import shutil


def revert(logger: logging.Logger):
    if not logger:
        logger = logging

    logger.info("DnDGMod by TotallyNotSeth\n\n")
    pck_path = files.get_dndg_pck_path()
    logger.debug(f"D&DG .pck path: {pck_path}")
    exe_path = pck_path.parent / "DnDG_64.exe"
    data_directory = files.get_appdata_directory()
    logger.debug(f"AppData directory: {data_directory}")

    logger.info("Copying DnDG_64.pck")
    shutil.copy(data_directory / "DnDG_vanilla.pck", pck_path)
    logger.info("Copying DnDG_64.exe")
    shutil.copy(data_directory / "DnDG_vanilla.exe", exe_path)
    logger.info("\nRevert Complete")
