from PIL import Image
import math
from pathlib import Path
import jinja2
import re


class Spritesheet:
    """A generic Godot spritesheet manager

    Manages Godot-style spritesheets. Should be subclassed for specific spritesheet types.
    """

    def __init__(self, spritesheet_path: Path, sprite_width: int, sprite_height: int):
        # TODO: More documentation
        self.sprite_width = sprite_width
        self.sprite_height = sprite_height
        self.spritesheet_path = spritesheet_path
        self.new_art = {}
        self.art_meta = []

    def add_art(self, id_: int, card_art_path: Path):
        self.new_art[id_] = card_art_path

    def update_spritesheet(self):
        if len(self.new_art) == 0:
            return
        with Image.open(self.spritesheet_path) as spritesheet:
            width, height = spritesheet.size
            new_spritesheet = Image.new("RGBA", (width,
                                                 height + 89 * math.ceil(
                                                     float(len(self.new_art)) / 13.0
                                                 )))
            new_spritesheet.paste(spritesheet, (0, 0, width, height))
        current_x, current_y = 0, height
        for id_, art_path in sorted(self.new_art.items(), key=lambda x: x[0]):
            with Image.open(art_path) as art:
                new_spritesheet.paste(art, (current_x, current_y,
                                            current_x + self.sprite_width, current_y + self.sprite_height))
            self.art_meta.append((id_, (current_x, current_y)))
            current_x += self.sprite_width
            if current_x >= width:
                current_x, current_y = 0, current_y + self.sprite_height
        new_spritesheet.save(self.spritesheet_path)
        # new_spritesheet.show()

    def update_tres(self, tres_path: Path):
        raise NotImplementedError


class CardSpritesheet(Spritesheet):
    CARD_WIDTH, CARD_HEIGHT = 57, 89

    def __init__(self, spritesheet_path: Path, jinja2_env: jinja2.Environment):
        super().__init__(spritesheet_path, self.CARD_WIDTH, self.CARD_HEIGHT)
        self.j2 = jinja2_env

    def update_tres(self, tres_path: Path):
        if len(self.art_meta) == 0:
            return
        with open(tres_path) as f:
            tres = f.read()
        tres = tres[:tres.find("[resource]") - 1]
        new_tres = self.j2.get_template("card_art_sprite_frames.tres.j2").render(
            other_sub_resources=tres, art_meta=self.art_meta, CARD_WIDTH=self.sprite_width,
            CARD_HEIGHT=self.sprite_height
        )
        new_tres = re.sub(r"load_steps=\d+", f"load_steps={self.art_meta[-1][0] + 2}", new_tres)
        with open(tres_path, "w") as f:
            f.write(new_tres)


if __name__ == "__main__":
    ss = Spritesheet(
        Path(r"C:\Users\sethe\AppData\Local\TotallyNotSeth\DnDGMod\decomped_src\assets\art\card_sprite_sheet.png")
    )
    for i in range(222, 237):
        ss.add_art(i, Path(r"C:\Users\sethe\AppData\Local\TotallyNotSeth\DnDGMod\test.png"))
    ss.update_spritesheet()
    ss.update_tres(
        Path(r"C:\Users\sethe\AppData\Local\TotallyNotSeth\DnDGMod\decomped_src\assets\art\card_art_sprite_frames.tres")
    )
