from .revert import revert
from .patch import patch
from .compile import compile_

import typer

def cycle(
        ctx: typer.Context
):
    revert(ctx)
    patch(ctx)
    compile_(ctx)
