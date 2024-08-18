import logging

from ..util import files

import subprocess
import shutil


def decompile(logger: logging.Logger = None):
    """Decompile Dungeons & Degenerate Gamblers."""
    if not logger:
        logger = logging

    logger.info("DnDGMod by TotallyNotSeth\n\n")

    data_directory = files.get_appdata_directory(logger=logger)
    logger.debug(f"AppData Directory: {data_directory}")
    dependencies_directory = data_directory / "dependencies"

    gdre_tools_path = dependencies_directory / "gdre_tools.exe"
    output_directory = data_directory / "src"
    output_directory.mkdir(exist_ok=True, parents=True)
    pck_path = files.get_dndg_pck_path()

    new_pck_path = data_directory / "DnDG_vanilla.pck"
    shutil.copy(pck_path, new_pck_path)
    new_exe_path = data_directory / "DnDG_vanilla.exe"
    shutil.copy(pck_path.parent / "DnDG_64.exe", new_exe_path)
    logger.info("Clearing output directory")
    shutil.rmtree(output_directory)
    logger.info("Decompiling D&DG with GDRE Tools (this may take a moment)")
    print([gdre_tools_path, "--headless", f"--recover={new_pck_path}",
                                f"--output-dir={output_directory}"])
    process = subprocess.Popen([gdre_tools_path, "--headless", f"--recover={new_pck_path}",
                                f"--output-dir={output_directory}"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    with process.stdout:
        for line in iter(process.stdout.readline, b''):  # b'\n'-separated lines
            logger.debug(line.decode("utf-8"))

    logger.info("Grabbing export presets")
    shutil.copy(dependencies_directory / "export_presets.cfg", output_directory / "export_presets.cfg")

    if not (templates_directory := files.get_godot_data_directory() / "templates" / "3.5.3.stable").exists():
        logging.info("Grabbing export templates")
        templates_directory.mkdir(parents=True)
        for template in ["windows_32_debug.exe", "windows_64_debug.exe",
                         "windows_32_release.exe", "windows_64_release.exe"]:
            shutil.copy(dependencies_directory / template, templates_directory / template)

    logger.info("Enabling GodotSteam")
    if not (output_directory / "addons" / "godotsteam").exists():
        shutil.copytree(dependencies_directory / "godotsteam", output_directory / "addons" / "godotsteam")
    shutil.copy(dependencies_directory / "project.godot", output_directory / "project.godot")

    logger.info("\nDecompile Complete")
