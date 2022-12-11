import json
from typing import Optional

import aiofiles

flair_dict: dict[str, str] = {}


async def load_flairs(file_path: Optional[str] = None) -> None:
    """Loads flairs from specified path to a global variable.

    :returns: None

    """
    global flair_dict
    async with aiofiles.open(file_path or "data_dictionaries/flairs_dict.json", "r") as fp:
        rank_dict = json.loads(await fp.read())

        for key, value in rank_dict.items():
            flair_dict[key] = value


async def get_flair_name(flair_text: str) -> str:
    """Gets the flair full name from flair id.

    :param flair_text: flair id used in reddit to show emojis

    :returns: flair full name

    """
    return flair_dict.get(flair_text, "None")
