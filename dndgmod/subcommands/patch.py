import logging
import os
from pathlib import Path

import jinja2
import yaml
import typer

from ..util.spritesheet import Spritesheet

FIRST_CARD = 222

class InvalidConfigurationError(Exception):
    pass

def clean_dict(dictionary):
    to_return = dict()
    for key, value in dictionary.items():
        key = key.lower().strip()
        if type(value) is dict:
            value = clean_dict(value)
        to_return[key] = value
    return to_return

def patch(
        ctx: typer.Context,
):
    """Patch the decompiled source code with installed mods."""
    card_number = FIRST_CARD - 1
    logger: logging.Logger = ctx.obj["logger"]
    data_directory: Path = ctx.obj["data_directory"]
    decompiled_src = data_directory / "decomped_src"
    effect_resources = decompiled_src / "card_effect_resources"
    card_list = decompiled_src / "singletons" / "CardList.gd"
    mods = (Path(f.path).resolve(strict=True) for f in os.scandir(data_directory / "mods") if f.is_dir())
    builtin_templates = jinja2.Environment(loader=jinja2.PackageLoader("dndgmod", "templates"))
    ss = Spritesheet(decompiled_src / "assets" / "art" / "card_sprite_sheet.png")

    for mod in mods:
        j2 = jinja2.Environment(loader=jinja2.FileSystemLoader(mod / "src"), trim_blocks=True, lstrip_blocks=True)
        j2.globals["wait_for"] = builtin_templates.get_template("wait_for.gd.j2").module.wait_for

        with open(mod / "mod.yaml") as f:
            metadata = yaml.safe_load(f)
        if metadata["exports"] != ["cards"]:
            raise InvalidConfigurationError("During the alpha phase, mods can only export cards")
        logger.info(f"Loaded \"{metadata['name']}\" configuration")

        with open(mod / "cards.yaml") as f:
            cards = yaml.safe_load(f)
        for name, card_data in cards.items():
            card_number += 1
            card_data = clean_dict(card_data)
            events = []

            for trigger, source in card_data["triggers"].items():
                events.append((trigger, j2.get_template(source).render()))
            on_event = builtin_templates.get_template("on_event.gd.j2").module.on_event
            with open(effect_resources / f"CardEffect{card_number}.gd", "w") as f:
                f.write(builtin_templates.get_template("CardEffectXXX.gd.j2").render(events=events, on_event=on_event))
            with open(effect_resources / f"card_effect_{card_number}.tres", "w") as f:
                f.write(builtin_templates.get_template("card_effect_XXX.tres.j2").render(id=card_number))
            with open(card_list) as f:
                card_list_contents = f.read()
            with open(card_list, "w") as f:
                entry = (builtin_templates.get_template("card_list_entry.j2")
                         .render(name=name, value=card_data["value"], id=card_number,
                                 description=card_data["description"]))
                card_list_contents = "},\n}".join(card_list_contents.rsplit("}\n}", 1))
                card_list_contents = entry.join(card_list_contents.rsplit("}", 1))
                f.write(card_list_contents + "\n}")

            ss.add_art(card_number, mod / "res" / card_data["image"])
    ss.update_spritesheet()
    ss.update_tres(decompiled_src / "assets" / "art" / "card_art_sprite_frames.tres")
