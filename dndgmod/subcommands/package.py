from zipfile import ZipFile

import os
import subprocess

from ..util import files


def package(slug, zip_file_path, open_explorer: bool = False):
    data_directory = files.get_appdata_directory()
    mod_directory = data_directory / "mods" / slug

    if not os.path.exists(mod_directory):
        raise FileNotFoundError(f"Directory {mod_directory} does not exist!")

    with ZipFile(zip_file_path, "w") as archive:
        for file_path in mod_directory.rglob("*"):
            archive.write(file_path, arcname=file_path.relative_to(mod_directory))

    if open_explorer:
        subprocess.Popen(f'explorer /select,"{zip_file_path.replace('/', '\\')}"')
