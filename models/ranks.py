import json

import aiofiles
from attrs import define


@define(kw_only=True)
class Rank:
    value: int
    name: str
    message: str


rank_list: list[Rank] = []


async def load_ranks() -> None:
    """Loads rank from specified path to a global variable.

    :returns: None

    """
    global rank_list
    async with aiofiles.open("data_dictionaries/ranks_dict.json", "r") as fp:
        rank_dict = json.loads(await fp.read())

        for key, value in rank_dict.items():
            rank_list.append(Rank(name=key, value=value["value"], message=value["message"]))


def rank_name(based_count: int, user: str) -> str:
    """Gets the user rank name from their based count.

    :param based_count: user based count
    :param user: username, used if based count is above 10_000

    :returns: rank which user is at

    """
    if based_count >= 10_000:
        return f"u/{user}'s Mom"

    for rank_index, rank in enumerate(rank_list):
        if based_count == rank.value:
            return rank_list[rank_index].name
        elif based_count < rank.value:
            return rank_list[rank_index - 1].name

    raise ValueError("No ranks for the given based count.")


def rank_message(based_count: int) -> str:
    """Gets the user rank message from their based count.

    :param based_count: user based count

    :returns: rank message of rank which user is at

    """

    if based_count >= 10_000:
        return "You have spent too much time collecting Based counts. Go touch grass or something."

    for r in rank_list:
        if based_count == r.value:
            return r.message
    raise ValueError("No ranks for the given based count.")
