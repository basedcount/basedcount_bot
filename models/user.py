from __future__ import annotations

from typing import Any, Optional

from attrs import define, field

from models.pill import Pill
from models.ranks import rank_list, load_ranks, rank_name


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
    user_id: str
    username: str
    based_count: int
    user_flair: str
    political_compass_values: tuple[str, str]
    sappy_values: tuple[str, str, str]
    based_time: list[int] = field(factory=list)
    pills: list[Pill] = field(factory=list)

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
            user_id=user_dict["id"],
            username=user_dict["name"],
            based_count=user_dict["count"],
            user_flair=user_dict["flair"],
            political_compass_values=user_dict["compass"],
            sappy_values=user_dict["sappy"],
            based_time=user_dict["basedTime"],
            pills=pills,
        )
        return user_instance

    def get_rank_name(self) -> str:
        """Gets the user rank name from their based count.

        :returns: rank which user is at

        """
        if rank_list:
            load_ranks()
        return rank_name(self.based_count, self.username)

    def format_pills(self) -> str:
        """Formats the pills into a nice string which is replied back to the user

        :returns: str object with pill count and link to website to view all the pills

        """
        pills = f"{len(self.pills):,}" if self.pills else "None"
        return f"[{pills} | View pills.](https://basedcount.com/u/{self.username}/)"

    def format_compass(self) -> str:
        """Gets the political compass from the raw value from political compass and sapply values.

        :returns: str object containing the compass of the user

        """
        compass_reply = ""
        if self.political_compass_type is not None:
            compass_reply = f"{self.political_compass_type}\n\n"
        if self.sappy_values_type is not None:
            compass_reply += f"{self.sappy_values_type}\n\n"
        return compass_reply
