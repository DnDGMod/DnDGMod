from pregex.core.groups import Backreference, Capture
from pregex.core.quantifiers import Optional, Indefinite, OneOrMore
from pregex.core.classes import AnyDigit, AnyWhitespace, AnyUppercaseLetter, AnyLowercaseLetter, AnyLetter

from os import PathLike
import typing


def add_encounter_to_room(room_list_file: PathLike, room_name: str, encounter_name: str):
    existing_room_pattern = ("var " + room_name.capitalize() +
                             "Rooms = {" + OneOrMore(Indefinite(AnyWhitespace()) +
                                                     OneOrMore(AnyUppercaseLetter() | "_") + " = \"" +
                                                     OneOrMore(AnyLowercaseLetter() | "_") + "\"" + Optional(",")))
    with open(room_list_file) as f:
        room_list_contents = f.read()
    encounter_name = encounter_name.replace(" ", "_")
    existing_room = existing_room_pattern.get_matches(room_list_contents)[0]

    with open(room_list_file, "w") as f:
        f.write(room_list_contents.replace(existing_room, existing_room +
                                           f",\n\tENCOUNTER_{encounter_name.upper()} = \""
                                           f"{room_name.lower()}_{encounter_name.lower()}\""))


def add_encounter_to_random_pool(room_list_file: PathLike, room_name: str, encounter_name: str,
                                 difficulty: typing.Optional[str]):
    random_encounter_pool_pattern = ("var " + room_name.lower().replace(" ", "_") + "_" + (difficulty
                                     if difficulty else "easy") + "_random_encounters = [" +
                                                        OneOrMore(Indefinite(AnyWhitespace()) +
                                                                  OneOrMore(AnyLetter() | "_" | ".") +
                                                                  Optional(",")))
    with open(room_list_file) as f:
        room_list_contents = f.read()
    encounter_name = encounter_name.replace(" ", "_")
    existing_pool = random_encounter_pool_pattern.get_matches(room_list_contents)[0]
    with open(room_list_file, "w") as f:
        f.write(room_list_contents.replace(existing_pool, existing_pool +
                                           f",\n\t{"".join(word.capitalize() for word in room_name.split())}Rooms"
                                           f".ENCOUNTER_{encounter_name.upper()}"))
