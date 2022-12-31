import asyncio
import time
from os import getenv

import aioschedule as schedule
from dotenv import load_dotenv
from utility_functions import get_mongo_client, get_mongo_collection, send_message_to_admin

load_dotenv("../.env")


async def send_cheating_report() -> None:
    async with get_mongo_client() as mongo_client:
        based_history_collection = await get_mongo_collection("basedHistory", mongo_client=mongo_client)
        based_history = await based_history_collection.find({}).to_list(length=None)

        report_list = []
        for based_transaction in based_history:
            if based_transaction.get("count", 0) > 5:
                report_list.append(f"- {based_transaction['from']} based {based_transaction['to']} {based_transaction['count']} times")

        report = "\n".join(report_list)
        await send_message_to_admin("Cheating Report", report, getenv("REDDIT_USERNAME", "basedcount_bot"))


async def backup_databased() -> None:
    return None


async def task_scheduler() -> None:
    cheating_report_task = asyncio.create_task(send_cheating_report())
    backup_task = asyncio.create_task(backup_databased())
    await cheating_report_task
    await backup_task


def main() -> None:
    asyncio.run(send_cheating_report())
    schedule.every(5).seconds.do(task_scheduler)
    while True:
        asyncio.run(schedule.run_pending())
        time.sleep(0.1)


if __name__ == '__main__':
    main()
