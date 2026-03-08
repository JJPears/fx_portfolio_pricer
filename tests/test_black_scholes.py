from src.pricing.black_scholes import price_fx_option, _calculate_d1_d2
from src.common.enums import OptionType
import numpy as np
import pytest


DIFF_TOLERANCE = 1e-4


def test_calculate_d1_d2_known_values():
    d1, d2 = _calculate_d1_d2(
        spot=1.10, strike=1.12, vol=0.11, rate_dom=0.02, rate_foreign=0.01, expiry=0.25
    )
    expected_d1 = -0.254655
    expected_d2 = -0.309655
    assert d1 == pytest.approx(expected_d1, DIFF_TOLERANCE)
    assert d2 == pytest.approx(expected_d2, DIFF_TOLERANCE)


def test_d2_is_d1_minus_vol_sqrt_t():
    """d2 = d1 - vol * sqrt(T) by definition"""
    vol, expiry = 0.11, 0.25
    d1, d2 = _calculate_d1_d2(1.10, 1.12, vol, 0.02, 0.01, expiry)
    assert d2 == pytest.approx(d1 - vol * np.sqrt(expiry), DIFF_TOLERANCE)


def test_call_pv():
    result = price_fx_option(
        trade_id="T000001",
        spot=1.10,
        strike=1.12,
        vol=0.11,
        rate_dom=0.02,
        rate_foreign=0.01,
        expiry=0.25,
        notional=1_000_000,
        option_type=OptionType.CALL,
    )
    expected_pv = 16639.78
    assert result.pv == pytest.approx(expected_pv, DIFF_TOLERANCE)


def test_put_pv():
    result = price_fx_option(
        trade_id="T000002",
        spot=1.10,
        strike=1.10,
        vol=0.12,
        rate_dom=0.02,
        rate_foreign=0.01,
        expiry=0.50,
        notional=500_000,
        option_type=OptionType.PUT,
    )
    expected_pv = 17140.97
    assert result.pv == pytest.approx(expected_pv, DIFF_TOLERANCE)


def test_pv_always_positive():
    """Option PV can never be negative"""
    for option_type in [OptionType.CALL, OptionType.PUT]:
        result = price_fx_option(
            trade_id="TEST",
            spot=1.10,
            strike=1.12,
            vol=0.11,
            rate_dom=0.02,
            rate_foreign=0.01,
            expiry=0.25,
            notional=1_000_000,
            option_type=option_type,
        )
        assert result.pv >= 0


def test_higher_vol_increases_pv():
    """Higher volatility always increases option value"""
    low_vol = price_fx_option(
        trade_id="TEST",
        spot=1.10,
        strike=1.12,
        vol=0.10,
        rate_dom=0.02,
        rate_foreign=0.01,
        expiry=0.25,
        notional=1_000_000,
        option_type=OptionType.CALL,
    )
    high_vol = price_fx_option(
        trade_id="TEST",
        spot=1.10,
        strike=1.12,
        vol=0.20,
        rate_dom=0.02,
        rate_foreign=0.01,
        expiry=0.25,
        notional=1_000_000,
        option_type=OptionType.CALL,
    )
    assert high_vol.pv > low_vol.pv


def test_longer_expiry_increases_pv():
    """Longer expiry always increases option value"""
    short = price_fx_option(
        trade_id="TEST",
        spot=1.10,
        strike=1.12,
        vol=0.11,
        rate_dom=0.02,
        rate_foreign=0.01,
        expiry=0.25,
        notional=1_000_000,
        option_type=OptionType.CALL,
    )
    long = price_fx_option(
        trade_id="TEST",
        spot=1.10,
        strike=1.12,
        vol=0.11,
        rate_dom=0.02,
        rate_foreign=0.01,
        expiry=1.0,
        notional=1_000_000,
        option_type=OptionType.CALL,
    )
    assert long.pv > short.pv


def test_call_delta_between_0_and_1():
    result = price_fx_option(
        trade_id="TEST",
        spot=1.10,
        strike=1.12,
        vol=0.11,
        rate_dom=0.02,
        rate_foreign=0.01,
        expiry=0.25,
        notional=1_000_000,
        option_type=OptionType.CALL,
    )
    assert 0 < result.delta < 1


def test_put_delta_between_minus1_and_0():
    result = price_fx_option(
        trade_id="TEST",
        spot=1.10,
        strike=1.12,
        vol=0.11,
        rate_dom=0.02,
        rate_foreign=0.01,
        expiry=0.25,
        notional=1_000_000,
        option_type=OptionType.PUT,
    )
    assert -1 < result.delta < 0


def test_itm_call_has_higher_delta_than_otm():
    """ITM call should have higher delta than OTM call"""
    itm = price_fx_option(
        trade_id="TEST",
        spot=1.10,
        strike=1.08,
        vol=0.11,
        rate_dom=0.02,
        rate_foreign=0.01,
        expiry=0.25,
        notional=1_000_000,
        option_type=OptionType.CALL,
    )
    otm = price_fx_option(
        trade_id="TEST",
        spot=1.10,
        strike=1.15,
        vol=0.11,
        rate_dom=0.02,
        rate_foreign=0.01,
        expiry=0.25,
        notional=1_000_000,
        option_type=OptionType.CALL,
    )
    assert itm.delta > otm.delta


def test_vega_always_positive():
    """Vega is always positive for both calls and puts"""
    for option_type in [OptionType.CALL, OptionType.PUT]:
        result = price_fx_option(
            trade_id="TEST",
            spot=1.10,
            strike=1.12,
            vol=0.11,
            rate_dom=0.02,
            rate_foreign=0.01,
            expiry=0.25,
            notional=1_000_000,
            option_type=option_type,
        )
        assert result.vega > 0


def test_call_itm_when_spot_above_strike():
    result = price_fx_option(
        trade_id="TEST",
        spot=1.15,
        strike=1.10,
        vol=0.11,
        rate_dom=0.02,
        rate_foreign=0.01,
        expiry=0.25,
        notional=1_000_000,
        option_type=OptionType.CALL,
    )
    assert result.itm is True


def test_put_itm_when_spot_below_strike():
    result = price_fx_option(
        trade_id="TEST",
        spot=1.05,
        strike=1.10,
        vol=0.11,
        rate_dom=0.02,
        rate_foreign=0.01,
        expiry=0.25,
        notional=1_000_000,
        option_type=OptionType.PUT,
    )
    assert result.itm is True


def test_call_otm_when_spot_below_strike():
    result = price_fx_option(
        trade_id="TEST",
        spot=1.10,
        strike=1.15,
        vol=0.11,
        rate_dom=0.02,
        rate_foreign=0.01,
        expiry=0.25,
        notional=1_000_000,
        option_type=OptionType.CALL,
    )
    assert result.itm is False
