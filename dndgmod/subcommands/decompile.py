from .._util.find import find_dndg

import subprocess
from typing import Annotated

import typer

def decompile(
        ctx: typer.Context
):
    """Decompile Dungeons & Degenerate Gamblers Modloader"""
    dndg_path = find_dndg()
    data_directory = ctx.obj["data_directory"]
    gdre_tools_path = data_directory / "dependencies" / "gdre_tools.exe"
    output_directory = data_directory / "decomped_src"
    subprocess.run([gdre_tools_path, "--headless", f"--recover={dndg_path}", f"--output-dir={output_directory}"])
