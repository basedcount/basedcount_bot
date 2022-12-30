from __future__ import annotations

import asyncio
import re
from typing import Awaitable, Callable

import aiofiles
from asyncpraw import Reddit
from asyncpraw.models import Message, Comment, Submission
from asyncprawcore.exceptions import AsyncPrawcoreException
from dotenv import load_dotenv
from yaml import safe_load

from bot_commands import get_based_count, most_based, based_and_pilled, my_compass, remove_pill, add_to_based_history
from utility_functions import create_logger, create_reddit_instance, send_message_to_admin

load_dotenv()


def exception_wrapper(func: Callable[[Reddit], Awaitable[None]]) -> Callable[[Reddit], Awaitable[None]]:
    """Decorator to handle the exceptions and to ensure the code doesn't exit unexpectedly.

    :param func: function that needs to be called

    :returns: wrapper function
    :rtype: Callable[[Reddit], Awaitable[None]]

    """

    async def wrapper(reddit_instance: Reddit) -> None:
        while True:
            try:
                await func(reddit_instance)
            except AsyncPrawcoreException:
                main_logger.exception("AsyncPrawcoreException", exc_info=True)
            except Exception:
                main_logger.critical("Serious Exception", exc_info=True)

    return wrapper


async def bot_commands(command: Message | Comment, command_body_lower: str) -> None:
    """Responsible for the basic based count bot commands

    :param command: Reddit post that triggered the command, could be a message or comment
    :param command_body_lower: The body of that message or command

    :returns: None

    """

    if command_body_lower.startswith("/"):
        main_logger.info(f"Received {type(command).__name__} from {command.author}, {command_body_lower}")

    if command_body_lower.startswith("/info"):
        async with aiofiles.open("data_dictionaries/bot_replies.yaml", "r") as fp:
            replies = safe_load(await fp.read())
            await command.reply(replies.get("info_message"))

    elif command_body_lower.startswith("/mybasedcount"):
        my_based_count = await get_based_count(user_name=command.author.name, is_me=True)
        await command.reply(my_based_count)

    elif result := re.match(r"/basedcount\s*(u/)?([A-Za-z0-9_-]+)", command.body, re.IGNORECASE):
        user_name = result.group(2)
        user_based_count = await get_based_count(user_name=user_name, is_me=False)
        await command.reply(user_based_count)

    elif command_body_lower.startswith("/mostbased"):
        await command.reply(await most_based())

    elif command_body_lower.startswith("/removepill"):
        response = await remove_pill(user_name=command.author.name, pill=command_body_lower.replace("/removepill ", ""))
        await command.reply(response)

    elif command_body_lower.startswith("/mycompass"):
        response = await my_compass(user_name=command.author.name, compass=command_body_lower.replace("/mycompass ", ""))
        await command.reply(response)


@exception_wrapper
async def check_mail(reddit_instance: Reddit) -> None:
    """Checks the Reddit mail every after and replies to the users.

    :param reddit_instance: The Reddit Instance from AsyncPraw. Used to make API calls.

    :returns: Nothing is returned

    """
    async for message in reddit_instance.inbox.unread(limit=None):  # Message
        # Ignore the comments
        if not isinstance(message, Message):
            await message.mark_read()
            continue

        message_subject_lower = message.subject.lower()
        message_body_lower = message.body.lower()

        if "suggestion" in message_subject_lower:
            forward_msg_task = asyncio.create_task(
                send_message_to_admin(message_subject=message.subject, message_body=message.body, author_name=message.author.name)
            )
            reply_task = asyncio.create_task(message.reply("Thank you for your suggestion. I have forwarded it to a human operator."))
            await forward_msg_task
            await reply_task
        elif "question" in message_subject_lower:
            forward_msg_task = asyncio.create_task(
                send_message_to_admin(message_subject=message.subject, message_body=message.body, author_name=message.author.name)
            )
            reply_task = asyncio.create_task(
                message.reply("Thank you for your question. I have forwarded it to a human operator, and I should reply shortly with an answer.")
            )
            await forward_msg_task
            await reply_task
        else:
            await bot_commands(message, message_body_lower)

        await message.mark_read()
    await asyncio.sleep(5)


BASED_VARIATION = (
    "Oj +1 byczq +1",
    "Oj+1byczq+1",
    "basado",
    "basat",
    "basato",
    "baseado",
    "based",
    "baserad",
    "baseret",
    "basert",
    "basiert",
    "baste",
    "basé",
    "baza",
    "bazat",
    "bazirano",
    "bazita",
    "bazowane",
    "berdasar",
    "fondatum",
    "fundiert",
    "gebaseerd",
    "gebasseerd",
    "na základě",
    "oparte",
    "perustunut",
    "perustuvaa",
    "založené",
    "Базирано",
    "основано",
    "מבוסס",
    "ベース",
    "基于",
)

BASED_REGEX = re.compile(f"({'|'.join(BASED_VARIATION)})\\b(?!\\s*(on|off))", re.IGNORECASE)
PILL_REGEX = re.compile("(?<=(and|but))(.+)pilled", re.IGNORECASE)


async def has_commands_checks_passed(comment: Comment, parent_info: dict[str, str]) -> bool:
    """Runs checks for self based/pills, unflaired users, and cheating in general

    :param comment: Comment which triggered the bot command
    :param parent_info: The parent comment/submission info.

    :returns: True if checks passed and False if checks failed

    """
    main_logger.info(f"Based Comment: {comment.body} from: u/{comment.author.name} to: u/{parent_info['parent_author']}")
    if comment.author.name == parent_info["parent_author"] or comment.author.name == "basedcount_bot":
        return False

    # check for unflaired users, the author_flair_text is empty str or None
    if not parent_info["parent_flair"]:
        return False

    # Check if people aren't just giving each other low effort based
    if parent_info["parent_body"].startswith(BASED_VARIATION) and len(parent_info["parent_body"]) < 50:
        return False

    asyncio.create_task(add_to_based_history(comment.author.name, parent_info["parent_author"]))
    return True


async def get_parent_info(comment: Comment) -> dict[str, str]:
    """Gets the parent comment/submission information and returns the data in dict.

    :param comment: Comment which triggered the bot command and whose parent data will be checked

    :returns: dict with all the information such as author name and content

    """
    parent_post = await comment.parent()
    await parent_post.load()
    parent_author = parent_post.author.name
    parent_body = "submission" if isinstance(parent_post, Submission) else parent_post.body.lower()
    parent_flair = parent_post.author_flair_text
    link = parent_post.permalink
    return {"parent_author": parent_author, "parent_body": parent_body, "parent_flair": parent_flair, "link": link}


@exception_wrapper
async def read_comments(reddit_instance: Reddit) -> None:
    """Checks comments as they come on r/PoliticalCompassMemes and performs actions accordingly.

    :param reddit_instance: The Reddit Instance from AsyncPraw. Used to make API calls.

    :returns: Nothing is returned

    """
    main_logger.info(f"Logged into {await reddit_instance.user.me()} Account.")
    pcm_subreddit = await reddit_instance.subreddit("PoliticalCompassMemes")
    async for comment in pcm_subreddit.stream.comments(skip_existing=True):  # Comment
        if comment.author.name in ["basedcount_bot", "flair-checking-bot"]:
            continue

        # Reddit fancy pants editor inserts the &#x200b; (Zero-width space) characters.
        # This can cause issue for pill extraction, if there is a bunch of space at the start of comment.
        comment_body_lower = comment.body.lower().replace("&#x200b;", "")
        if re.match(BASED_REGEX, comment_body_lower.replace("\n", "")):
            parent_info = await get_parent_info(comment)
            # Skip Unflaired scums and low effort based
            if not await has_commands_checks_passed(comment, parent_info):
                main_logger.info("Checks failed")
                continue
            main_logger.info("Checks passed")

            pill = None
            first_non_empty_line = next(line for line in comment_body_lower.splitlines() if line)
            if "pilled" in first_non_empty_line.lower():
                pill_match = re.search(PILL_REGEX, first_non_empty_line)
                if pill_match is not None:
                    clean_pill = pill_match.group(2).strip(" -")  # strips both space and - character
                    if len(clean_pill) < 70:
                        pill = {"name": clean_pill, "commentID": comment.id, "fromUser": comment.author.name, "date": comment.created_utc, "amount": 1}

            reply_message = await based_and_pilled(parent_info["parent_author"], parent_info["parent_flair"], pill)
            if reply_message is not None:
                await comment.reply(reply_message)
        else:
            await bot_commands(comment, comment_body_lower)


async def main() -> None:
    await asyncio.gather(
        check_mail(await create_reddit_instance()),
        read_comments(await create_reddit_instance()),
    )


if __name__ == "__main__":
    main_logger = create_logger(__name__)
    asyncio.run(main())
