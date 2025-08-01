from __future__ import annotations

from pydantic import BaseModel


class Record(BaseModel):
    subdomain: str
    value: str
    type: str

    def __hash__(self) -> int:
        return hash(self.subdomain)

    def __eq__(self, other) -> bool:
        other = Record.model_validate(other)
        return (
            self.subdomain == other.subdomain
            and self.value.strip(".") == other.value.strip(".")
            and self.type == other.type
        )

    def __str__(self) -> str:
        return f"[bold blue]{self.type}[/]: {self.subdomain} ➡️ {self.value}"
