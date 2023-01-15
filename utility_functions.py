from __future__ import annotations

from contextlib import asynccontextmanager
from logging import getLogger, Logger, config
from os import getenv

from asyncpraw import Reddit
from asyncpraw.reddit import Redditor
from colorlog import ColoredFormatter
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection

config.fileConfig("logging.conf")


@asynccontextmanager
async def get_mongo_client() -> AsyncIOMotorClient:
    """Returns the MongoDB AsyncIOMotorClient

    :returns: AsyncIOMotorClient object
    :rtype: AsyncIOMotorClient

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


@asynccontextmanager
async def create_reddit_instance() -> Reddit:
    """Creates Reddit instance and returns the object

    :returns: Reddit instance object.

    """
    reddit = Reddit(
        client_id=getenv("REDDIT_CLIENT_ID"),
        client_secret=getenv("REDDIT_CLIENT_SECRET"),
        password=getenv("REDDIT_PASSWORD"),
        user_agent="BasedCount by CodapopKSP",
        username=getenv("REDDIT_USERNAME"),
    )

    try:
        yield reddit
    finally:
        await reddit.close()


async def send_message_to_admin(message_subject: str, message_body: str, author_name: str, reddit: Reddit) -> None:
    """Forwards the message to the bot admin specified in the environment variable

    :param message_subject: Subject of message
    :param message_body: Body of message
    :param author_name: Sender name, useful when forwarding messages
    :param reddit: Reddit Instance used to send message to Redditor

    :returns: None

    """
    bot_admin: Redditor = await reddit.redditor(getenv("BOT_ADMIN"))
    await bot_admin.message(subject=f"{message_subject} from {author_name}", message=message_body)


def create_logger(logger_name: str) -> Logger:
    """Creates logger and returns an instance of logging object.

    :returns: Logging Object.

    """

    log_format = "%(log_color)s[%(asctime)s] %(levelname)s [%(filename)s.%(funcName)s:%(lineno)d] %(message)s"
    logger = getLogger(logger_name)
    for handler in logger.handlers:
        handler.setFormatter(ColoredFormatter(log_format))

    return getLogger(logger_name)
