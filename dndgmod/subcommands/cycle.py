import subprocess

from .revert import revert
from .patch import patch
from .compile import compile_
from ..util import files

import typer

def cycle(
        ctx: typer.Context
):
    revert(ctx)
    patch(ctx)
    compile_(ctx)
    subprocess.run([files.find_dndg().parent / "DnDG_64.exe"])
