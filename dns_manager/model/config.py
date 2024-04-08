from __future__ import annotations

from pydantic import BaseModel


class Config(BaseModel):
    domain: str
    records: list[tuple[str | list[str], str | None]]
    ignore: list[str] | None = None
