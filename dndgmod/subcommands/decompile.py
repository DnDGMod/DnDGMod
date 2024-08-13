import logging

from ..util import files

import subprocess
import shutil


def decompile(logger: logging.Logger = None):
    """Decompile Dungeons & Degenerate Gamblers."""
    if not logger:
        logger = logging

    data_directory = files.get_appdata_directory(logger=logger)
    dependencies_directory = data_directory / "dependencies"

    gdre_tools_path = dependencies_directory / "gdre_tools.exe"
    output_directory = data_directory / "src"
    pck_path = files.get_dndg_pck_path()

    new_pck_path = data_directory / "DnDG_vanilla.pck"
    shutil.copy(pck_path, new_pck_path)
    new_exe_path = data_directory / "DnDG_vanilla.exe"
    shutil.copy(pck_path.parent / "DnDG_64.exe", new_exe_path)
    shutil.rmtree(output_directory)
    subprocess.run([gdre_tools_path, "--headless", f"--recover={new_pck_path}", f"--output-dir={output_directory}"])
    shutil.copy(dependencies_directory / "export_presets.cfg", output_directory / "export_presets.cfg")

    if not (templates_directory := files.get_godot_data_directory() / "templates" / "3.5.3.stable").exists():
        templates_directory.mkdir(parents=True)
        for template in ["windows_32_debug.exe", "windows_64_debug.exe",
                         "windows_32_release.exe", "windows_64_release.exe"]:
            shutil.copy(dependencies_directory / template, templates_directory / template)
