from __future__ import annotations

import asyncio
import random
import re
from contextlib import suppress
from time import time
from typing import Optional, Any
from urllib.parse import urlsplit, parse_qs

import aiofiles
import yaml
from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorClient
from pymongo import ReturnDocument

from models.flairs import get_flair_name
from models.ranks import rank_name, rank_message
from models.user import User
from utility_functions import get_mongo_collection, create_logger

bot_commands_logger = create_logger(__name__)


async def find_or_create_user_profile(user_name: str, users_collection: AsyncIOMotorCollection) -> dict[str, Any]:
    """Finds the user in the users_collection, or creates one if it doesn't exist using default values

    :param user_name: The user whose profile to find or create
    :param users_collection: The collection in which the profile will be searched or inserted

    :returns: Dict object with user profile info

    """
    profile: Optional[dict[str, Any]] = await users_collection.find_one({"name": re.compile(rf"^{user_name}$", re.I)})
    if profile is None:
        profile = await users_collection.find_one_and_update(
            {"name": user_name},
            {
                "$setOnInsert": {
                    "flair": "Unflaired",
                    "count": 0,
                    "pills": [],
                    "compass": [],
                    "sapply": [],
                    "basedTime": [],
                    "mergedAccounts": [],
                    "unsubscribed": False,
                }
            },
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
    return profile


async def based_and_pilled(
    user_name: str, user_flair_id: str, user_flair_text: str, pill: Optional[dict[str, str | int]], mongo_client: AsyncIOMotorClient
) -> Optional[str]:
    """Increments the based count and adds the pill to a user database in mongo

    :param user_name: user whose based count/pill will be added.
    :param user_flair_id: flair id of the user.
    :param user_flair_text: flair text as it appears on Reddit
    :param pill: name of the pill that will be added.
    :param mongo_client: MongoDB Client used to get the collections.

    :returns: Comment response for the user when based count is 1, multiple of 5 and when they reach a new rank

    """
    bot_commands_logger.info(f"based_and_pilled args: u/{user_name}, flair: {user_flair_id}, pill: {pill}")
    users_collection = await get_mongo_collection(collection_name="users", mongo_client=mongo_client)
    profile = await find_or_create_user_profile(user_name, users_collection)
    flair_name = await get_flair_name(user_flair_id) or user_flair_text
    bot_commands_logger.info(f"Flair class: {user_flair_id} -> Flair name: {flair_name}")
    bot_commands_logger.info(f"Based Count before: {profile['count']}")
    await asyncio.gather(
        add_based_count(user_name, flair_name, users_collection),
        add_pills(user_name, pill, users_collection),
    )
    profile = await find_or_create_user_profile(user_name, users_collection)
    bot_commands_logger.info(f"Based Count: {profile['count']}")

    user = User.from_data(profile)
    all_based_counts = await user.get_all_accounts_based_count(users_collection)
    combined_based_count = sum(map(lambda x: x[1], all_based_counts))
    combined_pills = await user.combined_formatted_pills(users_collection)
    combined_rank = await rank_name(combined_based_count, user_name)
    rank_up = await rank_message(combined_based_count)

    if user.based_count == 1:
        return (
            f"u/{user_name} is officially based! Their Based Count is now 1.\n\n"
            f"Rank: {combined_rank}\n\n"
            f"Pills: {combined_pills}\n\n"
            f"Compass: {user.format_compass()}\n\n"
            f"I am a bot. Reply /info for more info. Please join our [official pcm discord server](https://discord.gg/FyaJdAZjC4)."
        )
    elif user.based_count % 5 == 0:
        if rank_up is not None:
            # Reply if user reaches a new rank
            return (
                f"u/{user_name}'s Based Count has increased by 1. Their Based Count is now {user.based_count}.\n\n"
                f"Congratulations, u/{user_name}! You have ranked up to {combined_rank}! {rank_up}\n\n"
                f"Pills: {combined_pills}\n\n"
                f"Compass: {user.format_compass()}\n\n"
                f"I am a bot. Reply /info for more info. Please join our [official pcm discord server](https://discord.gg/FyaJdAZjC4)."
            )
        # normal reply
        return (
            f"u/{user_name}'s Based Count has increased by 1. Their Based Count is now {user.based_count}.\n\n"
            f"Rank: {combined_rank}\n\n"
            f"Pills: {combined_pills}\n\n"
            f"Compass: {user.format_compass()}\n\n"
            f"I am a bot. Reply /info for more info. Please join our [official pcm discord server](https://discord.gg/FyaJdAZjC4)."
        )
    return None


async def add_based_count(user_name: str, flair_name: str, users_collection: AsyncIOMotorCollection) -> None:
    """Increases the based count of user by one

    :param user_name: user whose based count will be increased
    :param flair_name: flair of the user.
    :param users_collection: The collection in which the profile will be updated

    :returns: None

    """
    await users_collection.update_one({"name": user_name}, {"$set": {"flair": flair_name}, "$inc": {"count": 1}, "$push": {"basedTime": int(time())}})


async def add_pills(user_name: str, pill: Optional[dict[str, str | int]], users_collection: AsyncIOMotorCollection) -> None:
    """Add the pill to the user database

    :param user_name: The user's whose pill will be added
    :param pill: pill that will be added
    :param users_collection: The collection in which the profile will be updated

    :returns: None

    """
    if pill is None:
        return None

    await users_collection.update_one({"name": user_name, "pills.name": {"$ne": pill["name"]}}, {"$push": {"pills": pill}})


async def add_to_based_history(user_name: str, parent_author: str, mongo_client: AsyncIOMotorClient) -> None:
    """Adds the based count record to based history database, so it can be sent to mods for cheating report

    :param user_name: user who gave the based and pills
    :param parent_author: user who received the based
    :param mongo_client: MongoDB Client used to get the collections
    :type mongo_client: AsyncIOMotorClient

    :returns: None

    """
    based_history_collection = await get_mongo_collection(collection_name="basedHistory", mongo_client=mongo_client)
    await based_history_collection.update_one({"to": parent_author, "from": user_name}, {"$inc": {"count": 1}}, upsert=True)


async def most_based() -> str:
    """Returns the link to the basedcount.com leaderboard.

    :returns: Str object containing the top 10 most based users

    """
    return "See the Based Count Leaderboard at https://basedcount.com/leaderboard"


async def get_based_count(user_name: str, mongo_client: AsyncIOMotorClient, is_me: bool = False) -> str:
    """Retrieves the Based Count for the given username.

    :param user_name: Username whose based count will be retrieved
    :param mongo_client: MongoDB Client used to get the collections
    :param is_me: Flag to indicate if a user is requesting their own based count

    :returns: str object with based count summary of the user

    """
    users_collection = await get_mongo_collection(collection_name="users", mongo_client=mongo_client)
    profile = await users_collection.find_one({"name": re.compile(rf"^{user_name}$", re.I)})

    if profile is not None:
        user = User.from_data(profile)

        all_based_counts = await user.get_all_accounts_based_count(users_collection)
        combined_based_count = sum(map(lambda x: x[1], all_based_counts))
        combined_pills = await user.combined_formatted_pills(users_collection)
        combined_rank = await rank_name(combined_based_count, user_name)

        build_username = f"u/{profile['name']}'s"
        reply_message = (
            f"{'Your' if is_me else build_username} Based Count is {combined_based_count}\n\n"
            f"Rank: {combined_rank}\n\n"
            f"Pills: {combined_pills}\n\n"
            f"{user.format_compass()}"
        )

        if user.merged_accounts:
            merged_acc_summary = "\n\n".join([f"- [{x[0]}](https://basedcount.com/u/{x[0]}) {x[1]} based & {x[2]} pills" for x in all_based_counts])
            merged_account_reply = f"Based and Pill Count breakdown\n\n{merged_acc_summary}"
            reply_message = f"{reply_message}\n\n{merged_account_reply}"

    else:
        async with aiofiles.open("data_dictionaries/bot_replies.yaml", "r") as fp:
            replies = yaml.safe_load(await fp.read())
        if is_me:
            reply_message = random.choice(replies.get("my_based_no_user_reply"))
        else:
            reply_message = random.choice(replies.get("based_count_no_user_reply"))
    return reply_message


async def my_compass(user_name: str, compass: str, mongo_client: AsyncIOMotorClient) -> str:
    """Parses the Political Compass/Sapply Values url and saves to compass values in database

    :param user_name: User whose compass will be updated
    :param compass: The url given by the user
    :param mongo_client: MongoDB Client used to get the collections

    :returns: str message from parsed data

    """
    users_collection = await get_mongo_collection(collection_name="users", mongo_client=mongo_client)
    profile = await find_or_create_user_profile(user_name, users_collection)
    split_url = urlsplit(compass)
    root_domain = split_url.netloc or split_url.path
    url_query = parse_qs(split_url.query)

    with suppress(KeyError):
        if "sapplyvalues.github.io" in root_domain:
            sv_eco_type = url_query["right"][0]
            sv_soc_type = url_query["auth"][0]
            sv_prog_type = url_query["prog"][0]
            profile["sapply"] = [sv_prog_type, sv_soc_type, sv_eco_type]
            bot_commands_logger.info(f"Sapply Values: {profile['sapply']}")
            await users_collection.update_one({"name": user_name}, {"$set": {"sapply": profile["sapply"]}})
            user = User.from_data(profile)
            return f"Your Sapply compass has been updated.\n\n{user.sappy_values_type}"

        elif "politicalcompass.org" in root_domain:
            compass_economic_axis = url_query["ec"][0]
            compass_social_axis = url_query["soc"][0]
            profile["compass"] = [compass_economic_axis, compass_social_axis]
            bot_commands_logger.info(f"PCM Values: {profile['compass']}")
            await users_collection.update_one({"name": user_name}, {"$set": {"compass": profile["compass"]}})
            user = User.from_data(profile)
            return f"Your political compass has been updated.\n\n{user.political_compass_type}"

    return (
        "Sorry, but that isn't a valid URL. "
        "Please copy/paste the entire test result URL from politicalcompass.org or sapplyvalues.github.io, starting with 'https'."
    )


async def remove_pill(user_name: str, pill: str, mongo_client: AsyncIOMotorClient) -> str:
    """Removes the pill by adding deleted = True field in the dict obj

    :param user_name: The user whose pill is going to be removed
    :param pill: Name of the pill being removed
    :param mongo_client: MongoDB Client used to get the collections

    :returns: Message that is sent back to the user

    """
    users_collection = await get_mongo_collection(collection_name="users", mongo_client=mongo_client)
    res = await users_collection.find_one_and_update(
        {"name": user_name, "pills.name": pill}, {"$set": {"pills.$.deleted": True}}, return_document=ReturnDocument.AFTER
    )
    if not res:
        return "You do not have that pill!"
    else:
        return f'"{pill}" pill removed. See your pills at https://basedcount.com/u/{user_name}'


async def set_subscription(subscribe: bool, user_name: str, mongo_client: AsyncIOMotorClient) -> str:
    """Sets the user's unsubscribed bool to True or False

    :param subscribe: Boolean indicating whether to set the status to subscribed or unsubscribed
    :param user_name: The user whose subscription status is being changed
    :param mongo_client: MongoDB Client used to get the collections

    :returns: Message that is sent back to the user

    """
    users_collection = await get_mongo_collection(collection_name="users", mongo_client=mongo_client)
    profile = await find_or_create_user_profile(user_name, users_collection)
    res = await users_collection.update_one({"name": profile["name"]}, {"$set": {"unsubscribed": not subscribe}}, return_document=ReturnDocument.AFTER)
    if res:
        return "You have unsubscribed from basedcount_bot." if subscribe else "Thank you for subscribing to basedcount_bot!"
    else:
        return "Error: Please contact the mods."


async def check_unsubscribed(username: str, mongo_client: AsyncIOMotorClient) -> bool:
    """Check the value of the "unsubscribed" field for a user with the given username in a MongoDB collection.

    If the "unsubscribed" field is missing, add it to the user document and set its value to False.

    :param username: The username to search for in the collection.
    :param mongo_client: A MotorAsyncIOMotorClient instance representing the MongoDB client.

    :returns: The value of the "unsubscribed" field for the user, or False if the user doesn't exist or the "unsubscribed" field is missing.

    """
    users_collection = await get_mongo_collection(collection_name="users", mongo_client=mongo_client)
    profile = await users_collection.find_one({"name": username})

    if "unsubscribed" in profile:
        unsub: bool = profile["unsubscribed"]
        return unsub
    else:
        # If the "unsubscribed" field is missing, add it and set its value to False
        await users_collection.update_one({"name": username}, {"$set": {"unsubscribed": False}})
        return False
