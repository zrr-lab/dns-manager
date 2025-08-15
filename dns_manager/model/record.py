from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class Record(BaseModel):
    subdomain: str
    value: str
    type: Literal["A", "AAAA", "CNAME", "TXT"]

    def __hash__(self) -> int:
        return hash(self.subdomain)

    def __eq__(self, other) -> bool:
        other = Record.model_validate(other)

        if self.subdomain != other.subdomain or self.type != other.type:
            return False

        if self.type == "CNAME":
            return self.value.removesuffix(".") == other.value.removesuffix(".")
        else:
            return self.value == other.value

    def __str__(self) -> str:
        return f"[bold blue]{self.type}[/]: {self.subdomain} ➡️ {self.value}"
