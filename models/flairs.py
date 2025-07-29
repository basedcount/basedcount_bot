from __future__ import annotations

import json

import aiofiles

flair_dict: dict[str, str] = {}


async def load_flairs() -> None:
    """Loads flairs from specified path to a global variable.

    :returns: None

    """
    global flair_dict
    async with aiofiles.open("data_dictionaries/flairs_dict.json") as fp:
        rank_dict = json.loads(await fp.read())

        for key, value in rank_dict.items():
            flair_dict[key] = value


async def get_flair_name(user_flair_id: str | None) -> str | None:
    """Gets the flair full name from flair id.

    :param user_flair_id: flair id of the user

    :returns: flair full name

    """
    if not flair_dict:
        await load_flairs()

    # If flair_text is None or Empty String
    if not user_flair_id:
        return "Unflaired"

    return flair_dict.get(user_flair_id)
