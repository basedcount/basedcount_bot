import random

import aiofiles
import yaml
import re

from models.user import User
from utility_functions import get_mongo_collection


async def most_based() -> str:
    """Returns the top 10 most based users of all time.

    :returns: Str object containing the top 10 most based users

    """
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
