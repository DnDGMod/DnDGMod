from pregex.core.groups import Backreference, Capture
from pregex.core.quantifiers import Optional, Indefinite
from pregex.core.classes import AnyDigit, AnyWhitespace

from os import PathLike
import re


def card_id_string(contents):
    return '"' + str(contents) + '"' + Optional(",") + Indefinite(AnyWhitespace())


def increase_replacement(counterfeiter_file: PathLike, cards_list: list[int]):
    pattern = Capture("var standard_card_ids_in_order = [" + Indefinite(card_id_string(AnyDigit() * 3)) +
                      card_id_string(cards_list[0]))
    replacement = Backreference(1)
    for card in cards_list[1:]:
        replacement += f'"{card}", '
    with open(counterfeiter_file) as f:
        script = f.read()
    with open(counterfeiter_file, "w") as f:
        f.write(re.sub(pattern.get_pattern(), replacement.get_pattern(), script))


def decrease_replacement(counterfeiter_file: PathLike, cards_list: list[int]):
    pattern = (Capture("var standard_card_ids_in_order = [" + Indefinite(card_id_string(AnyDigit() * 3))) +
               Capture(card_id_string(cards_list[0])))
    replacement = Backreference(1)
    for card in cards_list[:0:-1]:
        replacement += f'"{card}", '
    replacement += Backreference(2)
    with open(counterfeiter_file) as f:
        script = f.read()
    with open(counterfeiter_file, "w") as f:
        f.write(re.sub(pattern.get_pattern(), replacement.get_pattern(), script))


if __name__ == "__main__":
    from pathlib import Path
    decrease_replacement(Path(r"/modified_src/events/EventCounterfeiterIncreaseDecrease.gd"), ["245", "420", "500"])
