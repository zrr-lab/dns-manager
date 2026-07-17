from __future__ import annotations

from ipaddress import ip_address
from typing import Literal, override

from pydantic import BaseModel, ValidationError, model_validator


class Record(BaseModel):
    subdomain: str
    value: str
    type: Literal["A", "AAAA", "CNAME", "TXT"]

    @model_validator(mode="after")
    def normalize_ip_value(self) -> Record:
        if self.type in {"A", "AAAA"}:
            address = ip_address(self.value)
            expected_version = 4 if self.type == "A" else 6
            if address.version != expected_version:
                raise ValueError(f"{self.type} record requires an IPv{expected_version} address")
            self.value = str(address)
        return self

    @override
    def __hash__(self) -> int:
        return hash(self.subdomain)

    @override
    def __eq__(self, other: object) -> bool:
        if isinstance(other, Record):
            candidate = other
        else:
            try:
                candidate = Record.model_validate(other)
            except (ValidationError, TypeError, ValueError):
                return NotImplemented

        if self.subdomain != candidate.subdomain or self.type != candidate.type:
            return False

        if self.type == "CNAME":
            return self.value.removesuffix(".") == candidate.value.removesuffix(".")
        return self.value == candidate.value

    @override
    def __str__(self) -> str:
        return f"[bold blue]{self.type}[/]: {self.subdomain} ➡️ {self.value}"
