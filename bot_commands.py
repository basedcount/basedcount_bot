from __future__ import annotations

import asyncio
import random
import re
from contextlib import suppress
from typing import Optional
from urllib.parse import urlsplit, parse_qs

import aiofiles
import yaml
from pymongo import ReturnDocument

from models.user import User
from models.flairs import get_flair_name
from models.ranks import rank_name, rank_message
from utility_functions import get_mongo_collection


async def based_and_pilled(user_name: str, flair_css_class: str, pill: Optional[dict[str, str | int]]) -> Optional[str]:
    add_based_count_task = asyncio.create_task(add_based_count(user_name, flair_css_class))
    add_pils_task = asyncio.create_task(add_pils(user_name, pill))
    await add_based_count_task
    await add_pils_task

    data_based = await get_mongo_collection(collection_name="users")
    profile = await data_based.find_one({"name": re.compile(rf"^{user_name}", re.I)})
    user = User.from_data(profile)
    rank = await rank_name(user.based_count, user_name)
    rank_up = await rank_message(user.based_count)

    if user.based_count == 1:
        return (
            f"u/{user_name} is officially based! Their Based Count is now 1.\n\n"
            f"Rank: {rank}\n\n"
            f"Pills: {user.format_pills()}\n\n"
            f"Compass: {user.format_compass()}\n\n"
            f"I am a bot. Reply /info for more info."
        )
    elif user.based_count % 5 == 0:
        if rank_up is not None:
            # Reply if user reaches a new rank
            return (
                f"u/{user_name}'s Based Count has increased by 1. Their Based Count is now {user.based_count}.\n\n"
                f"Congratulations, u/{user_name}! You have ranked up to {rank}! {rank_up}"
                f"Pills: {user.format_pills()}\n\n"
                f"Compass: {user.format_compass()}\n\n"
                f"I am a bot. Reply /info for more info."
            )
        # normal reply
        return (
            f"u/{user_name}'s Based Count has increased by 1. Their Based Count is now {user.based_count}.\n\n"
            f"Rank: {rank}\n\n"
            f"Pills: {user.format_pills()}\n\n"
            f"Compass: {user.format_compass()}\n\n"
            f"I am a bot. Reply /info for more info."
        )
    return None


async def add_based_count(user_name: str, flair_css_class: str) -> None:
    """Increases the based count of user by one

    :param user_name: user whose based count will be increased
    :param flair_css_class: the flair class of the user

    :returns: None

    """
    data_based = await get_mongo_collection(collection_name="users")
    flair_name = await get_flair_name(flair_css_class)
    await data_based.find_one_and_update(
        {"name": user_name},
        {"$set": {"flair": flair_name}, "$inc": {"count": 1}, "$setOnInsert": {"pills": [], "compass": [], "sapply": []}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )


async def add_to_based_history(user_name: str, parent_author: str) -> None:
    """Adds the based count record to based history database, so it can be sent to mods for cheating report

    :param user_name: user who gave the based and pills
    :param parent_author: user who received the based

    :returns: None

    """
    based_history = await get_mongo_collection(collection_name="users")
    await based_history.find_one_and_update({"name": user_name}, {"$inc": {parent_author: 1}}, upsert=True)


async def add_pils(user_name: str, pill: Optional[dict[str, str | int]]) -> None:
    """Add the pill to the user database

    :param user_name: The user's whose pill will be added
    :param pill: pill that will be added

    :returns: None

    """
    if pill is None:
        return None

    data_based = await get_mongo_collection(collection_name="users")
    await data_based.find_one_and_update({"name": user_name, "pills.name": {"$ne": pill["name"]}}, {"$push": {"pills": pill}})


async def most_based() -> str:
    """Returns the top 10 most based users of all time.

    :returns: Str object containing the top 10 most based users

    """
    # TODO: Update to reflect the account merging
    data_based = await get_mongo_collection(collection_name="users")
    top_ten = await data_based.find().sort("count", -1).limit(10).to_list(length=None)

    most_count_flair = []
    for pos, result in enumerate(top_ten, start=1):
        most_count_flair.append(f"{pos}. {{name}} || {{count}} | {{flair}}".format(**result))
    return "--The Top 10 Most Based Users--\n\n" + "\n\n".join(most_count_flair)


async def get_based_count(user_name: str, is_me: bool = False) -> str:
    """Retrieves the Based Count for the given username.

    :param user_name: Username whose based count will be retrieved
    :param is_me: Flag to indicate if a user is requesting their own based count

    :returns: str object with based count summary of the user

    """
    data_based = await get_mongo_collection(collection_name="users")
    profile = await data_based.find_one({"name": re.compile(rf"^{user_name}", re.I)})
    if profile is not None:
        user = User.from_data(profile)
        reply_message = (
            f"{'Your' if is_me else user_name} Based Count is {user.based_count}.\n\n"
            f"Rank: {await user.get_rank_name()}.\n\n"
            f"Pills: {user.format_pills()}.\n\n"
            f"{user.format_compass()}"
        )
    else:
        async with aiofiles.open("data_dictionaries/bot_replies.yaml", "r") as fp:
            replies = yaml.safe_load(await fp.read())
        if is_me:
            reply_message = random.choice(replies.get("my_based_no_user_reply"))
        else:
            reply_message = random.choice(replies.get("based_count_no_user_reply"))
    return reply_message


async def my_compass(user_name: str, compass: str) -> str:
    """Parses the Political Compass/Sapply Values url and saves to compass values in database

    :param user_name: User whose compass will be updated
    :param compass: The url given by the user

    :returns: str message from parsed data

    """
    data_based = await get_mongo_collection(collection_name="users")
    profile = await data_based.find_one({"name": re.compile(rf"^{user_name}", re.I)})
    if profile is None:
        await data_based.update_one({"name": user_name}, {"$set": {"flair": "Unflaired", "count": 0, "pills": [], "compass": [], "sapply": []}}, upsert=True)

    split_url = urlsplit(compass)
    root_domain = split_url.netloc or split_url.path
    url_query = parse_qs(split_url.query)

    with suppress(KeyError):
        if "sapplyvalues.github.io" in root_domain:
            sv_eco_type = url_query["right"][0]
            sv_soc_type = url_query["auth"][0]
            sv_prog_type = url_query["prog"][0]
            profile["sapply"] = [sv_prog_type, sv_soc_type, sv_eco_type]
            await data_based.update_one({"name": user_name}, {"$set": {"sapply": profile["sapply"]}})
            user = User.from_data(profile)
            return f"Your Sapply compass has been updated.\n\n{user.sappy_values_type}"

        elif "politicalcompass.org" in root_domain:
            compass_economic_axis = url_query["ec"][0]
            compass_social_axis = url_query["soc"][0]
            profile["compass"] = [compass_economic_axis, compass_social_axis]
            await data_based.update_one({"name": user_name}, {"$set": {"compass": profile["compass"]}})
            user = User.from_data(profile)
            return f"Your political compass has been updated.\n\n{user.political_compass_type}"

    return (
        "Sorry, but that isn't a valid URL. "
        "Please copy/paste the entire test result URL from politicalcompass.org or sapplyvalues.github.io, starting with 'https'."
    )


async def remove_pill(user_name: str, pill: str) -> str:
    """Removes the pill by adding deleted = True field in the dict obj

    :param user_name: The user whose pill is going to be removed
    :param pill: Name of the pill being removed

    :returns: Message that is sent back to the user

    """
    data_based = await get_mongo_collection(collection_name="users")
    res = await data_based.find_one_and_update(
        {"name": re.compile(rf"^{user_name}", re.I), "pills.name": pill}, {"$set": {"pills.$.deleted": True}}, return_document=ReturnDocument.AFTER
    )
    if not res:
        return "You do not have that pill!"
    else:
        return f'"{pill}" pill removed. See your pills at https://basedcount.com/u/{user_name}'
