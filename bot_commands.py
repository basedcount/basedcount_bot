import random

import aiofiles
import yaml

from models.user import User
from utility_functions import get_mongo_collection


async def get_based_count(user_name: str, is_me: bool = False) -> str:
    """Retrieves the Based Count for the given username.

    :param user_name: Username whose based count will be retrieved
    :param is_me: Flag to indicate if a user is requesting their own based count

    :returns: str object with based count summary of the user

    """
    data_based = await get_mongo_collection(collection_name="users")
    profile = await data_based.find_one({"name": user_name})
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
