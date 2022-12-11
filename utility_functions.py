from __future__ import annotations

import logging
from logging.config import fileConfig
from os import getenv

from asyncpraw import Reddit
from asyncpraw.reddit import Redditor
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection


async def get_mongo_collection(collection_name: str) -> AsyncIOMotorCollection:
    """Returns the user databased from dataBased Cluster from MongoDB

    :returns: Returns a Collection from Mongo DB

    """
    cluster = AsyncIOMotorClient(getenv("MONGO_PASS"))
    data_based = cluster["dataBased"]
    return data_based[collection_name]


async def create_reddit_instance() -> Reddit:
    """Creates Reddit instance and returns the object

    :returns: Reddit instance object.

    """
    return Reddit(
        client_id=getenv("REDDIT_CLIENT_ID"),
        client_secret=getenv("REDDIT_CLIENT_SECRET"),
        password=getenv("REDDIT_PASSWORD"),
        user_agent="BasedCount by CodapopKSP",
        username=getenv("REDDIT_USERNAME"),
    )


async def send_message_to_admin(message_subject: str, message_body: str, author_name: str) -> None:
    """Forwards the message to the bot admin specified in the environment variable

    :param message_subject: Subject of message
    :param message_body: Body of message
    :param author_name: Sender name, useful when forwarding messages

    :returns: None

    """
    bot_admin: Redditor = await (await create_reddit_instance()).redditor(getenv("BOT_ADMIN"))
    await bot_admin.message(subject=f"{message_subject} from {author_name}", message=message_body)


def create_logger() -> logging.Logger:
    """Creates logger and returns an instance of logging object.

    :returns: Logging Object.

    """
    fileConfig("logging.conf")
    logger = logging.getLogger("basedcount_bot")
    return logger
