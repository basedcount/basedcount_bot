from os import getenv

from utility_functions import send_message_to_admin, get_mongo_collection


async def check_for_cheating(user_name: str, parent_author_name: str) -> None:
    based_history = await get_mongo_collection(collection_name="basedHistory")
    await based_history.find_one_and_update({"name": user_name}, {"$inc": {parent_author_name: 1}}, upsert=True)


async def send_cheat_report() -> None:
    """Sends cheat report to the bot admins

    :returns: None

    """
    based_history = await get_mongo_collection(collection_name="basedHistory")
    user_profile = based_history.find({})

    content = ""
    for user in user_profile:
        for key in user:
            if key != "_id" and key != "name" and user[key] > 5:
                content += f"{user['name']} based {key} {user[key]} times.\n"

    if content != "":
        await send_message_to_admin(message_subject="Cheat Report", message_body=content, author_name=getenv("REDDIT_USERNAME", "basedcount_bot"))
