from __future__ import annotations

import asyncio
from typing import Any, Optional

from attrs import define, field
from motor.motor_asyncio import AsyncIOMotorCollection

from models.pill import Pill


def quadrant_name(compass_value: str, side1: str, side2: str) -> str:
    """Gets the quadrant name from the compass value provide and formats in a string

    :param compass_value: compass value is the coordinate position of where you lie on a Political Compass
    :param side1: One of the side from Political Compass (e.g. Left or Right) If side1 is Left, side2 is Right.
    :param side2: The other side from Political Compass

    :returns: quadrant name in formatted string

    """
    if "-" in compass_value:
        compass_value = compass_value.replace("-", "")
        return f"{side1} : {compass_value}"
    else:
        return f"{side2} : {compass_value}"


@define(kw_only=True)
class User:
    username: str
    based_count: int
    user_flair: str
    political_compass_values: tuple[str, str]
    sappy_values: tuple[str, str, str]
    based_time: list[int] = field(factory=list)
    pills: list[Pill] = field(factory=list)
    merged_accounts: list[str] = field(factory=list)

    # Post Init stuff
    political_compass_type: Optional[str] = field(default=None)
    sappy_values_type: Optional[str] = field(default=None)

    def __attrs_post_init__(self) -> None:
        if len(self.political_compass_values) >= 2:
            compass_economic_axis = self.political_compass_values[0]
            compass_social_axis = self.political_compass_values[1]

            pc_eco_type = quadrant_name(compass_economic_axis, "Left", "Right")
            pc_soc_type = quadrant_name(compass_social_axis, "Lib", "Auth")
            self.political_compass_type = f"Compass: {pc_soc_type} | {pc_eco_type}"

        if len(self.sappy_values) >= 3:
            sappy_values_economic_axis = self.sappy_values[2]
            sappy_values_social_axis = self.sappy_values[1]
            sappy_values_progressive_axis = self.sappy_values[0]

            sv_eco_type = quadrant_name(sappy_values_economic_axis, "Left", "Right")
            sv_soc_type = quadrant_name(sappy_values_social_axis, "Lib", "Auth")
            sv_prog_type = quadrant_name(sappy_values_progressive_axis, "Conservative", "Progressive")
            self.sappy_values_type = f"Sapply: {sv_soc_type} | {sv_eco_type} | {sv_prog_type}"

    @classmethod
    def from_data(cls, user_dict: dict[Any, Any]) -> User:
        pills = [Pill.from_data(pill=pill, owner_name=user_dict["name"]) for pill in user_dict["pills"]]
        user_instance = cls(
            username=user_dict["name"],
            based_count=user_dict["count"],
            user_flair=user_dict["flair"],
            political_compass_values=user_dict["compass"],
            sappy_values=user_dict["sapply"],
            based_time=user_dict.get("basedTime", []),
            pills=pills,
            merged_accounts=user_dict.get("mergedAccounts", []),
        )
        return user_instance

    def format_compass(self) -> str:
        """Gets the political compass from the raw value from political compass and sapply values.

        :returns: str object containing the compass of the user

        """
        compass_reply = ""
        if self.political_compass_type is not None:
            compass_reply = f"{self.political_compass_type}\n\n"
        if self.sappy_values_type is not None:
            compass_reply += f"{self.sappy_values_type}\n\n"
        return (
            compass_reply
            or "This user does not have a compass on record. "
            "Add compass to profile by replying with /mycompass politicalcompass.org url or sapplyvalues.github.io url.\n\n"
        )

    async def combined_formatted_pills(self, user_collection: AsyncIOMotorCollection) -> str:
        """Formats the pills from all merged accounts into a nice string which is replied back to the user

        :returns: str object with pill count and link to website to view all the pills

        """
        task_list = []
        for user_name in self.merged_accounts:
            task_list.append(user_collection.find_one({"name": user_name}))

        pills = []
        profile_list = await asyncio.gather(*task_list)
        for profile in profile_list:
            pills.extend(profile["pills"])

        combined_pill_count = len(pills) + len(self.pills)
        pill_str = f"{combined_pill_count:,}" if combined_pill_count > 0 else "None"
        return f"[{pill_str} | View pills](https://basedcount.com/u/{self.username}/)"

    async def get_all_accounts_based_count(self, user_collection: AsyncIOMotorCollection) -> list[tuple[str, int, int]]:
        """Gets the based count from all the all accounts (main + merged accounts)

        :param user_collection: Mongo db collection object which will be used to fetch data

        :returns: List of tuple containing username and the based count of that account

        """

        task_list = []
        for user_name in self.merged_accounts:
            task_list.append(user_collection.find_one({"name": user_name}))

        based_count_list = [(self.username, self.based_count, len(self.pills))]
        profile_list = await asyncio.gather(*task_list)
        for profile in profile_list:
            based_count_list.append((profile["name"], profile["count"], len(profile["pills"])))
        return based_count_list
