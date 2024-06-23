import logging
import os
from pathlib import Path
import shutil

import jinja2
import yaml
import typer

from ..util.spritesheet import Spritesheet
from ..util import files

FIRST_CARD = 274


class InvalidConfigurationError(Exception):
    pass


def clean_dict(dictionary):
    to_return = dict()
    for key, value in dictionary.items():
        key = key.lower().strip().replace(" ", "_")
        if type(value) is dict:
            value = clean_dict(value)
        to_return[key] = value
    return to_return


def patch(
        ctx: typer.Context,
):
    """Patch the decompiled source code with installed mods."""
    logger: logging.Logger = ctx.obj["logger"]
    data_directory: Path = ctx.obj["data_directory"]
    vanilla_src = data_directory / "src"
    modified_src = data_directory / "modified_src"
    shutil.rmtree(modified_src)
    shutil.copytree(vanilla_src, modified_src)

    effect_resources = modified_src / "card_effect_resources"
    card_list = modified_src / "singletons" / "CardList.gd"
    mods = (Path(f.path).resolve(strict=True) for f in os.scandir(data_directory / "mods") if f.is_dir())
    builtin_templates = jinja2.Environment(loader=jinja2.PackageLoader("dndgmod", "templates"))
    ss = Spritesheet(modified_src / "assets" / "art" / "card_sprite_sheet.png")

    for mod in mods:
        j2 = jinja2.Environment(loader=jinja2.BaseLoader())
        j2.globals["wait_for"] = builtin_templates.get_template("wait_for.gd.j2").module.wait_for  # type: ignore

        with open(mod / "mod.yaml") as f:
            metadata = clean_dict(yaml.safe_load(f))
        if metadata["exports"] != ["cards"]:
            raise InvalidConfigurationError("During the alpha phase, mods can only export cards")
        logger.info(f"Loaded \"{metadata['name']}\" configuration")

        with open(mod / "cards.yaml") as f:
            cards = yaml.safe_load(f)
        card_ids = {}
        for i, (_, card_data) in enumerate(cards.items()):
            if "identifier" in card_data:
                card_ids[card_data["identifier"]] = i + FIRST_CARD
        for i, (name, card_data) in cards.items():
            card_number = i + FIRST_CARD
            card_data = clean_dict(card_data)
            events = []

            if "triggers" in card_data:
                for trigger, source in card_data["triggers"].items():
                    with open(mod / "src" / source) as f:
                        template = f.read().replace("\n", "\n    ")
                    events.append((trigger, j2.from_string(template).render()))
                on_event = builtin_templates.get_template("on_event.gd.j2").module.on_event  # type: ignore
                with open(effect_resources / f"CardEffect{card_number}.gd", "w") as f:
                    f.write(builtin_templates.get_template("CardEffectXXX.gd.j2")
                            .render(events=events, on_event=on_event, card_ids=card_ids))
                with open(effect_resources / f"card_effect_{card_number}.tres", "w") as f:
                    f.write(builtin_templates.get_template("card_effect_XXX.tres.j2").render(id=card_number))
            with open(card_list) as f:
                card_list_contents = f.read()
            with open(card_list, "w") as f:
                entry = (builtin_templates.get_template("card_list_entry.j2")
                         .render(name=name, value=card_data["value"], suit=card_data.get("suit", "special"),
                                 id=card_number, description=card_data["description"],
                                 attributes=card_data.get("attributes", ["REWARD"]),
                                 collection_entry=42000 + card_number, flexible=card_data.get("flexible", None),
                                 keywords=card_data.get("keywords", None)))
                card_list_contents = "},\n}".join(card_list_contents.rsplit("}\n}", 1))
                card_list_contents = entry.join(card_list_contents.rsplit("}", 1))
                f.write(card_list_contents + "\n}")

            ss.add_art(card_number, mod / "res" / card_data["image"])
    ss.update_spritesheet()
    ss.update_tres(modified_src / "assets" / "art" / "card_art_sprite_frames.tres")
