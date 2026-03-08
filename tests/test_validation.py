import pytest
from pydantic import ValidationError
from src.models.models import FXOptionTrade
from src.common.enums import OptionType


def create_valid_trade(**overrides) -> dict:
    """Base valid trade — override fields to test specific validation"""
    base = {
        "trade_id": "T000001",
        "underlying": "EUR/USD",
        "notional": 1_000_000,
        "notional_ccy": "USD",
        "spot": 1.10,
        "strike": 1.12,
        "vol": 0.11,
        "rate_dom": 0.02,
        "rate_foreign": 0.01,
        "expiry": 0.25,
        "option_type": "Call",
    }
    return base | overrides


def test_valid_trade_parses_correctly():
    trade = FXOptionTrade(**create_valid_trade())
    assert trade.trade_id == "T000001"
    assert trade.option_type == OptionType.CALL


def test_underlying_must_be_ccy1_slash_ccy2():
    with pytest.raises(ValidationError):
        FXOptionTrade(**create_valid_trade(underlying="EURUSD"))


def test_underlying_normalised_to_uppercase():
    trade = FXOptionTrade(**create_valid_trade(underlying="eur/usd"))
    assert trade.underlying == "EUR/USD"


def test_notional_ccy_must_be_3_chars():
    with pytest.raises(ValidationError):
        FXOptionTrade(**create_valid_trade(notional_ccy="US"))


def test_notional_ccy_must_be_in_underlying():
    with pytest.raises(ValidationError):
        FXOptionTrade(**create_valid_trade(notional_ccy="JPY"))


def test_notional_must_be_positive():
    with pytest.raises(ValidationError):
        FXOptionTrade(**create_valid_trade(notional=-1_000_000))


def test_spot_must_be_positive():
    with pytest.raises(ValidationError):
        FXOptionTrade(**create_valid_trade(spot=0))


def test_strike_must_be_positive():
    with pytest.raises(ValidationError):
        FXOptionTrade(**create_valid_trade(strike=-1.0))


def test_vol_must_be_positive():
    with pytest.raises(ValidationError):
        FXOptionTrade(**create_valid_trade(vol=0))


def test_vol_cannot_exceed_3():
    with pytest.raises(ValidationError):
        FXOptionTrade(**create_valid_trade(vol=3.5))


def test_expiry_must_be_positive():
    with pytest.raises(ValidationError):
        FXOptionTrade(**create_valid_trade(expiry=0))


def test_option_type_case_insensitive():
    """OptionType enum should accept call/CALL/Call"""
    for value in ["call", "CALL", "Call"]:
        trade = FXOptionTrade(**create_valid_trade(option_type=value))
        assert trade.option_type == OptionType.CALL


def test_invalid_option_type_raises():
    with pytest.raises(ValidationError):
        FXOptionTrade(**create_valid_trade(option_type="Forward"))


def test_missing_field_raises():
    data = create_valid_trade()
    del data["vol"]
    with pytest.raises(ValidationError):
        FXOptionTrade(**data)