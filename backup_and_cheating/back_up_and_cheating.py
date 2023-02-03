from __future__ import annotations

import asyncio
import sys
import time
from os import getenv
from pathlib import Path
from traceback import format_exc

import aioschedule as schedule
from dotenv import load_dotenv

from backup_drive import backup_databased

sys.path.append(str(Path(sys.argv[0]).absolute().parent.parent))

from utility_functions import get_mongo_client, get_mongo_collection, send_message_to_admin, create_reddit_instance, send_traceback_to_discord, create_logger

load_dotenv("../.env")
backup_cheating_logger = create_logger(__name__)


async def send_cheating_report() -> None:
    """Sends the based history records to bot admin if a user has given another user more than 5 based

    :returns: None

    """
    async with get_mongo_client() as mongo_client:
        based_history_collection = await get_mongo_collection("basedHistory", mongo_client=mongo_client)
        based_history = await based_history_collection.find({}).to_list(length=None)

        sorted_transactions: list[tuple[str, str, int]] = []
        for based_transaction in based_history:
            if based_transaction.get("count", 0) > 5:
                sorted_transactions.append((based_transaction["from"], based_transaction["to"], based_transaction["count"]))

        sorted_transactions.sort(key=lambda x: x[2], reverse=True)
        report = "\n".join(f"- {x[0]} based {x[1]} {x[2]} times" for x in sorted_transactions)
        async with create_reddit_instance() as reddit:
            msg = "No user gave more than 5 based" if not report else report
            await send_message_to_admin("Cheating Report", msg, getenv("REDDIT_USERNAME", "basedcount_bot"), reddit=reddit)
        await based_history_collection.delete_many({})


async def backup() -> None:
    """Backs up the entire databased on Google Drive

    :returns: None

    """
    async with get_mongo_client() as mongo_client:
        users_collection = await get_mongo_collection("users", mongo_client=mongo_client)
        users = await users_collection.find({}).to_list(length=None)
        await asyncio.to_thread(backup_databased, users)


async def task_scheduler() -> None:
    backup_cheating_logger.info("Running Scheduled Task")
    try:
        cheating_report_task = asyncio.create_task(send_cheating_report())
        backup_task = asyncio.create_task(backup())
        await cheating_report_task
        await backup_task
    except Exception as exc:
        backup_cheating_logger.exception("Exception", exc_info=True)
        await send_traceback_to_discord(exception_name=type(exc).__name__, exception_message=str(exc), exception_body=format_exc())


def main() -> None:
    backup_cheating_logger.info("Started backup and cheating task...")
    schedule.every().day.at("00:00").do(task_scheduler)
    asyncio.run(task_scheduler())
    while True:
        asyncio.run(schedule.run_pending())
        time.sleep(0.1)


if __name__ == "__main__":
    main()
