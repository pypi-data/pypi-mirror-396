from typing import Any, Annotated, Literal
from pydantic import BaseModel, Field, field_validator
from ipaddress import ip_network, ip_address


# Shared literals to keep protocol/type values consistent across models
ProtocolLiteral = Literal["TCP", "UDP", "ICMP"]
CacherTypeLiteral = Literal["A2S", "Bedrock"]


## Rules
class RuleType(BaseModel):
    name: str
    description: str
    identifier: int
    allowed_protocols: list[ProtocolLiteral]


class RuleTypesResponse(BaseModel):
    rule_types: list[RuleType]
    message: str


class Rule(BaseModel):
    ip: str
    source_ip: str
    dst_port: Annotated[int, Field(ge=1, le=65535)]
    protocol: ProtocolLiteral
    action: str

    @field_validator("ip")
    @classmethod
    def ip_must_be_valid_ip(cls, v: str) -> str:
        # Single host IP expected here; normalize to canonical representation
        try:
            return str(ip_address(v))
        except Exception:
            raise ValueError(f"Invalid ip format (expected single IP): '{v}'")

    @field_validator("source_ip")
    @classmethod
    def source_ip_must_be_valid(cls, v: str) -> str:
        # Normalize common "any" IPv4 shorthands to full IPv4 any network
        if v in {"0", "0.0.0.0", "0.0.0.0/0"}:
            return "0.0.0.0/0"
        try:
            # Normalize to canonical network string; strict=False allows host IPs (e.g 127.0.0.1/24)
            return str(ip_network(v, strict=False))
        except Exception:
            raise ValueError(f"Invalid source_ip format (expected IP or CIDR): '{v}'")


class RuleResponse(BaseModel):
    rules: list[Rule]
    message: str


class AddRuleResponse(BaseModel):
    message: str
    rule: dict[str, Any]


class DeleteRuleResponse(BaseModel):
    message: str
    success: bool


## Cachers
class Cacher(BaseModel):
    ip: str
    dst_port: Annotated[int, Field(ge=1, le=65535)]
    type: CacherTypeLiteral

    @field_validator("ip")
    @classmethod
    def ip_must_be_valid_ip(cls, v: str) -> str:
        try:
            return str(ip_address(v))
        except Exception:
            raise ValueError(f"Invalid ip format (expected single IP): '{v}'")


class CachersResponse(BaseModel):
    message: str
    cachers: list[Cacher]


class AddCacherResponse(BaseModel):
    message: str
    success: bool


class DeleteCacherResponse(BaseModel):
    message: str = "Cacher deleted successfully."
    success: bool


## Attacks
class Attack(BaseModel):
    unix_start_time: int
    unix_end_time: int
    destination_ip: str
    max_packets_per_second: Annotated[float, Field(ge=0)]
    max_bits_per_second: Annotated[float, Field(ge=0)]

    @field_validator("destination_ip")
    @classmethod
    def destination_ip_must_be_valid_ip(cls, v: str) -> str:
        try:
            return str(ip_address(v))
        except Exception:
            raise ValueError(f"Invalid destination_ip format (expected single IP): '{v}'")

    @field_validator("unix_end_time")
    @classmethod
    def end_after_start(cls, v: int, info):
        start = info.data.get("unix_start_time")
        if isinstance(start, int) and v < start:
            raise ValueError("unix_end_time must be greater than or equal to unix_start_time")
        return v


class AttackResponse(BaseModel):
    attacks: list[Attack]
    message: str = "Successfully retrieved all attacks."
    success: bool = True
