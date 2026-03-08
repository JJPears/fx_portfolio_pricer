from pydantic import BaseModel, Field, field_validator, model_validator
from common.enums import OptionType
from dataclasses import dataclass


@dataclass(frozen=True)
class PricedOption:
    trade_id: str
    pv: float
    delta: float
    vega: float
    itm: bool


@dataclass(frozen=True)
class PortfolioSummary:
    notional_ccy: str
    total_pv: float
    total_delta: float
    total_vega: float


class FXOptionTrade(BaseModel):
    trade_id: str
    underlying: str
    notional: float = Field(gt=0)
    notional_ccy: str
    spot: float = Field(gt=0)
    strike: float = Field(gt=0)
    vol: float = Field(gt=0, le=3.0)
    rate_dom: float = Field(ge=-0.5, le=0.5)
    rate_foreign: float = Field(ge=-0.5, le=0.5)
    expiry: float = Field(gt=0)
    option_type: OptionType

    @field_validator("underlying")
    @classmethod
    def validate_underlying(cls, v: str) -> str:
        parts = v.split("/")
        if len(parts) != 2 or not all(len(p) == 3 for p in parts):
            raise ValueError(f"underlying must be in CCY1/CCY2 format, got {v}")
        return v.upper()

    @field_validator("notional_ccy")
    @classmethod
    def validate_notional_ccy(cls, v: str) -> str:
        if len(v) != 3:
            raise ValueError(f"notional_ccy must be a 3 letter currency code, got {v}")
        return v.upper()

    @model_validator(mode="after")
    def validate_notional_ccy_in_underlying(self) -> "FXOptionTrade":
        currencies = self.underlying.split("/")
        if self.notional_ccy not in currencies:
            raise ValueError(
                f"notional_ccy {self.notional_ccy} must be one of {currencies}"
            )
        return self