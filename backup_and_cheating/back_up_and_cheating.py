import asyncio
import time
from os import getenv

import aioschedule as schedule
from dotenv import load_dotenv

from backup_drive import backup_databased
from utility_functions import get_mongo_client, get_mongo_collection, send_message_to_admin, create_reddit_instance

load_dotenv("../.env")


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
            await send_message_to_admin("Cheating Report", report, getenv("REDDIT_USERNAME", "basedcount_bot"), reddit=reddit)
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
    cheating_report_task = asyncio.create_task(send_cheating_report())
    backup_task = asyncio.create_task(backup())
    await cheating_report_task
    await backup_task


def main() -> None:
    schedule.every(1).days.do(task_scheduler)
    while True:
        asyncio.run(schedule.run_pending())
        time.sleep(0.1)


if __name__ == "__main__":
    main()
