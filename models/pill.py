from __future__ import annotations

from typing import Any

from attrs import define


@define(frozen=True, kw_only=True)
class Pill:
    name: str
    comment_permalink: str
    from_user: str
    date: int
    amount: int
    owner_name: str

    @classmethod
    def from_data(cls, pill: dict[Any, Any], owner_name: str) -> Pill:
        return cls(
            name=pill["name"],
            comment_permalink=pill["commentID"],
            from_user=pill["fromUser"],
            date=pill["date"],
            amount=pill.get("amount", 1),
            owner_name=owner_name,
        )
