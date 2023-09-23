from __future__ import annotations

import json
from contextlib import asynccontextmanager
from logging import getLogger, Logger, config
from os import getenv
from pathlib import Path
from traceback import print_exc
from typing import Optional

import aiohttp
from aiohttp import ClientSession
from asyncpraw import Reddit
from asyncpraw.reddit import Redditor
from colorlog import ColoredFormatter
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection

Path("logs").mkdir(exist_ok=True)
conf_file = Path("logging.conf")
if conf_file.is_file():
    config.fileConfig(str(conf_file))
else:
    config.fileConfig(str(Path(__file__).parent / "logging.conf"))


async def post_to_pastebin(title: str, body: str) -> Optional[str]:
    """Uploads the text to PasteBin and returns the url of the Paste

    :param title: Title of the Paste
    :param body: Body of Paste

    :returns: url of Paste

    """
    login_data = {"api_dev_key": getenv("PASTEBIN_DEV_KEY"), "api_user_name": getenv("PASTEBIN_USERNAME"), "api_user_password": getenv("PASTEBIN_PASSWORD")}

    data = {
        "api_option": "paste",
        "api_dev_key": getenv("PASTEBIN_DEV_KEY"),
        "api_paste_code": body,
        "api_paste_name": title,
        "api_paste_expire_date": "1W",
        "api_user_key": None,
        "api_paste_format": "python",
    }

    try:
        async with ClientSession() as session:
            login_resp = await session.post("https://pastebin.com/api/api_login.php", data=login_data)
            if login_resp.status == 200:
                data["api_user_key"] = await login_resp.text()
                post_resp = await session.post("https://pastebin.com/api/api_post.php", data=data)
                if post_resp.status == 200:
                    return await post_resp.text()
    except aiohttp.ClientError:
        print_exc()
    return None


async def send_traceback_to_discord(exception_name: str, exception_message: str, exception_body: str) -> None:
    """Send the traceback of an exception to a Discord webhook.

    :param exception_name: The name of the exception.
    :param exception_message: A brief summary of the exception.
    :param exception_body: The full traceback of the exception.

    """
    paste_bin_url = await post_to_pastebin(f"{exception_name}: {exception_message}", exception_body)

    if paste_bin_url is None:
        return

    webhook = getenv("DISCORD_WEBHOOK", "deadass")
    data = {"content": f"[{exception_name}: {exception_message}]({paste_bin_url})", "username": "BasedCountBot"}
    async with ClientSession(headers={"Content-Type": "application/json"}) as session:
        async with session.post(url=webhook, data=json.dumps(data)):
            pass


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
