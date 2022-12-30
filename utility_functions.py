from __future__ import annotations

from contextlib import asynccontextmanager
from logging import getLogger, Logger, config
from os import getenv

from asyncpraw import Reddit
from asyncpraw.reddit import Redditor
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection


@asynccontextmanager
async def get_mongo_client() -> AsyncIOMotorClient:
    """Returns the MongoDB AsyncIOMotorClient

    :returns: AsyncIOMotorClient object

    """
    cluster = AsyncIOMotorClient(getenv("MONGO_PASS"))
    try:
        yield cluster["dataBased"]
    finally:
        cluster.close()


async def get_mongo_collection(collection_name: str, mongo_client: AsyncIOMotorClient) -> AsyncIOMotorCollection:
    """Returns the user databased from dataBased Cluster from MongoDB

    :returns: Returns a Collection from Mongo DB

    """
    return mongo_client[collection_name]


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


def create_logger(logger_name: str) -> Logger:
    """Creates logger and returns an instance of logging object.

    :returns: Logging Object.

    """
    config.fileConfig("logging.conf")
    return getLogger(logger_name)
