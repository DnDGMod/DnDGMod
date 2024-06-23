import re
from pathlib import Path
import os
import shutil


def find_dndg() -> Path:
    with open("C:/Program Files (x86)/Steam/steamapps/libraryfolders.vdf") as f:
        matches = re.finditer("\"path\"\t\t\"(.*?)\"", f.read())
    for match in matches:
        library = (Path(match.groups()[0]) / "steamapps" / "common").resolve(strict=True)
        dndg_path = library / "Dungeons &amp;amp; Degenerate Gamblers Demo" / "DnDG_64.pck"
        if dndg_path.exists():
            return dndg_path
    else:
        raise FileNotFoundError("Dungeons & Degenerate Gamblers could not be found. "
                                "Make sure it's installed via Steam!")


def nuke_directory(folder: Path):
    for filename in os.listdir(folder):
        file_path = folder / filename
        try:
            if file_path.is_file():
                os.unlink(file_path)
            elif file_path.is_dir():
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))
