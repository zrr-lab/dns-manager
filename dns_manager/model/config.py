from __future__ import annotations

from pydantic import BaseModel, Field


class Config(BaseModel):
    domain: str
    setter_name: str
    records: list[tuple[str | list[str], str | None]] = Field(default_factory=list)
    ignore: list[str] = Field(default_factory=list)
    # Load-time only; merged into records/ignore before the setter runs.
    # Defaults to records.<config-suffix> (e.g. records.toml) when omitted.
    records_files: list[str] | None = None
