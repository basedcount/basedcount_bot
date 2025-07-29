#!../.venv/bin/python
from __future__ import annotations

import asyncio
import concurrent.futures
import functools
import sys
from os import getenv
from pathlib import Path
from traceback import format_exc

from backup_drive import backup_databased
from dotenv import load_dotenv

sys.path.append(str(Path(sys.argv[0]).absolute().parent.parent))

from utility_functions import (
    create_logger,
    create_reddit_instance,
    get_mongo_client,
    get_mongo_collection,
    send_message_to_admin,
    send_traceback_to_discord,
    setup_logging,
)

load_dotenv("../.env")
setup_logging(str(Path(__file__).parent / "logging_config.json"))
backup_cheating_logger = create_logger(__name__)


MAX_BASED_COUNT = 5


async def send_cheating_report() -> None:
    """Sends the based history records to bot admin if a user has given another user more than 5 based.

    :returns: None

    """
    async with get_mongo_client() as mongo_client:
        based_history_collection = await get_mongo_collection("basedHistory", mongo_client=mongo_client)
        based_history = await based_history_collection.find({}).to_list(length=None)

        sorted_transactions = [
            (based_transaction["from"], based_transaction["to"], based_transaction["count"])
            for based_transaction in based_history
            if based_transaction.get("count", 0) > MAX_BASED_COUNT
        ]

        sorted_transactions.sort(key=lambda x: x[2], reverse=True)
        report = "\n".join(f"- {x[0]} based {x[1]} {x[2]} times" for x in sorted_transactions)
        async with create_reddit_instance() as reddit:
            msg = report if report else "No user gave more than 5 based"
            await send_message_to_admin("Cheating Report", msg, getenv("REDDIT_USERNAME", "basedcount_bot"), reddit=reddit)
        await based_history_collection.delete_many({})


async def backup() -> None:
    """Backs up the entire databased on Google Drive.

    :returns: None

    """
    async with get_mongo_client() as mongo_client:
        users_collection = await get_mongo_collection("users", mongo_client=mongo_client)
        users = await users_collection.find({}).to_list(length=None)

        loop = asyncio.get_running_loop()
        func_call = functools.partial(backup_databased, users)
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            await loop.run_in_executor(pool, func_call)


async def backup_and_cheating_runner() -> None:
    """Runs the scheduled backup and cheating report tasks concurrently, and logs any exceptions that occur during execution."""
    backup_cheating_logger.info("Running Scheduled Task")
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(send_cheating_report())
            tg.create_task(backup())
    except Exception as exc:
        backup_cheating_logger.exception("Exception")
        await send_traceback_to_discord(exception_name=type(exc).__name__, exception_message=str(exc), exception_body=format_exc())


def main() -> None:
    backup_cheating_logger.info("Started backup and cheating task...")
    asyncio.run(backup_and_cheating_runner())


if __name__ == "__main__":
    main()
