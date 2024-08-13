from zipfile import ZipFile
from pathlib import Path
import shutil

from ..exceptions import InvalidDnDGModZIPPackageFormatException
from ..util import files


def unpackage(zip_file_path: Path):
    data_directory = files.get_appdata_directory()
    mod_directory = data_directory / "mods" / zip_file_path.name.rstrip(".zip")
    with ZipFile(zip_file_path, "r") as archive:
        archive.extractall(mod_directory)
    if not (mod_directory / "mod.yaml").exists():
        if ((submod_directory := mod_directory / mod_directory.stem) / "mod.yaml").exists():
            shutil.move(submod_directory, mod_directory)
        else:
            shutil.rmtree(mod_directory)
            raise InvalidDnDGModZIPPackageFormatException("The provided .zip file was not in dndgmod format")
