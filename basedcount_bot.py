import asyncio
import re
from typing import Awaitable, Callable

from asyncpraw import Reddit
from asyncpraw.models import Message
from asyncprawcore.exceptions import AsyncPrawcoreException
from dotenv import load_dotenv
from yaml import safe_load

from bot_commands import get_based_count
from utility_functions import create_logger, create_reddit_instance, send_message_to_admin

load_dotenv()


def exception_wrapper(func: Callable[[Reddit], Awaitable[None]]) -> Callable[[Reddit], Awaitable[None]]:
    async def wrapper(reddit_instance: Reddit) -> None:
        try:
            await func(reddit_instance)
        except AsyncPrawcoreException:
            main_logger.exception("AsyncPrawcoreException", exc_info=True)
        except Exception:
            main_logger.critical("Serious Exception", exc_info=True)

    return wrapper


@exception_wrapper
async def check_mail(reddit_instance: Reddit) -> None:
    """Checks the Reddit mail every after and replies to the users.

    :param reddit_instance: The Reddit Instance from AsyncPraw. Used to make API calls.

    :returns: Nothing is returned

    """
    while True:
        async for message in reddit_instance.inbox.unread(limit=None):  # Message
            if not isinstance(message, Message):
                await reddit_instance.inbox.mark_read(message)
                continue

            message_subject = message.subject.lower()
            message_body = message.body.lower()
            main_logger.info(f"Received message from {message.author}, {message_subject}: {message_body}")

            if "suggestion" in message_subject:
                forward_msg_task = asyncio.create_task(
                    send_message_to_admin(message_subject=message.subject, message_body=message.body, author_name=message.author.name)
                )
                reply_task = asyncio.create_task(message.reply("Thank you for your suggestion. I have forwarded it to a human operator."))
                await forward_msg_task
                await reply_task
            elif "question" in message_subject:
                forward_msg_task = asyncio.create_task(
                    send_message_to_admin(message_subject=message.subject, message_body=message.body, author_name=message.author.name)
                )
                reply_coro = message.reply("Thank you for your question. I have forwarded it to a human operator, and I should reply shortly with an answer.")
                reply_task = asyncio.create_task(reply_coro)
                await forward_msg_task
                await reply_task

            if "/info" in message_body:
                with open("data_dictionaries/bot_replies.yaml", "r") as fp:
                    replies = safe_load(fp)
                    await message.reply(replies.get("info_message"))

            elif "/mybasedcount" in message_body:
                my_based_count = await get_based_count(user_name=message.author.name, is_me=True)
                await message.reply(my_based_count)

            elif "/basedcount" in message_body:
                if result := re.search(r"/basedcount\s*?(u/)?([A-Za-z0-9_-]+)", message.body, re.IGNORECASE):
                    user_name = result.group(2)
                    user_based_count = await get_based_count(user_name=user_name, is_me=False)
                    await message.reply(user_based_count)
                else:
                    await message.reply("Incorrect use of command. The command needs to be like /basedcount u/basedcount_bot.")

            elif "/mostbased" in message_body:
                await message.reply("Most Based")

            await message.mark_read()
        await asyncio.sleep(5)


@exception_wrapper
async def read_comments(reddit_instance: Reddit) -> None:
    """Checks comments as they come on r/PoliticalCompassMemes and performs actions accordingly.

    :param reddit_instance: The Reddit Instance from AsyncPraw. Used to make API calls.

    :returns: Nothing is returned

    """
    print(await reddit_instance.user.me())
    await asyncio.sleep(2)
    print("done comments")


async def main() -> None:
    await asyncio.gather(check_mail(await create_reddit_instance()), read_comments(await create_reddit_instance()))


if __name__ == "__main__":
    main_logger = create_logger()
    asyncio.run(main())
