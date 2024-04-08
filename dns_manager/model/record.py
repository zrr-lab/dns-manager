from __future__ import annotations

from pydantic import BaseModel


class Record(BaseModel):
    subdomain: str
    value: str
    type: str | None = None

    def __hash__(self) -> int:
        return hash(self.subdomain)

    def __eq__(self, other: Record) -> bool:
        return (
            self.subdomain == other.subdomain
            and self.value == other.value
            and self.type == other.type
        )

    def __str__(self) -> str:
        return f"[bold blue]{self.type}[/]: {self.subdomain} [bold blue]➡️[/] {self.value}"
