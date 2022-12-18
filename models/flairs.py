import json
from typing import Optional

import aiofiles

flair_dict: dict[str, str] = {}


async def load_flairs() -> None:
    """Loads flairs from specified path to a global variable.

    :returns: None

    """
    global flair_dict
    async with aiofiles.open("data_dictionaries/flairs_dict.json", "r") as fp:
        rank_dict = json.loads(await fp.read())

        for key, value in rank_dict.items():
            flair_dict[key] = value


async def get_flair_name(flair_text: Optional[str]) -> str:
    """Gets the flair full name from flair id.

    :param flair_text: flair id used in reddit to show emojis

    :returns: flair full name

    """

    if not flair_dict:
        await load_flairs()

    # If flair_text is None or Empty String
    if not flair_text:
        return "Unflaired"

    # If we can't find the full name for the flair_text, then the flair_text is itself returned
    return flair_dict.get(flair_text) or flair_text
