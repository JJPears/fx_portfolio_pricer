from pydantic import BaseModel
from enum import Enum


class OptionType(str, Enum):
    CALL = "Call"
    PUT = "Put"


class OptionTrade(BaseModel):
    trade_id: str
    underlying: str
    notional: float
    notional_ccy: str
    spot: float
    strike: float
    vol: float
    rate_dom: float
    rate_foreign: float
    expiry: float
    option_Type: OptionType