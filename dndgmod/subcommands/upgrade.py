import shutil
import tempfile
from pathlib import Path

import typer


def upgrade(ctx: typer.Context):
    data_directory = ctx.obj["data_directory"]
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_mods = Path(tmpdir) / 'mods'
        shutil.move(data_directory / "mods", tmp_mods)
        shutil.rmtree(data_directory)
        data_directory.mkdir(parents=True)
        shutil.move(tmp_mods, data_directory / "mods")
    (data_directory / "src").mkdir()
