import pytest
from src.models.models import FXOptionTrade, PricedOption
from src.portfolio_aggregator.aggregator import aggregate_by_currency
from src.common.enums import OptionType

DIFF_TOLERANCE = 1e-4


def create_trade(trade_id: str, notional_ccy: str) -> FXOptionTrade:
    underlying = "EUR/USD" if notional_ccy == "USD" else "USD/JPY"
    return FXOptionTrade(
        trade_id=trade_id,
        underlying=underlying,
        notional=1_000_000,
        notional_ccy=notional_ccy,
        spot=1.10 if notional_ccy == "USD" else 135.0,
        strike=1.12 if notional_ccy == "USD" else 136.0,
        vol=0.11,
        rate_dom=0.02,
        rate_foreign=0.01,
        expiry=0.25,
        option_type=OptionType.CALL,
    )


def create_priced_option(trade_id: str, pv: float, delta: float, vega: float) -> PricedOption:
    return PricedOption(trade_id=trade_id, pv=pv, delta=delta, vega=vega, itm=False)


def test_aggregates_into_correct_currency_buckets():
    trades = [
        create_trade("T001", "USD"),
        create_trade("T002", "USD"),
        create_trade("T003", "JPY"),
    ]
    results = [
        create_priced_option("T001", 1000.0, 0.4, 0.002),
        create_priced_option("T002", 2000.0, 0.5, 0.003),
        create_priced_option("T003", 500000.0, 0.45, 0.3),
    ]
    summaries = aggregate_by_currency(trades, results)
    assert len(summaries) == 2
    ccys = {s.notional_ccy for s in summaries}
    assert ccys == {"USD", "JPY"}


def test_usd_totals_correct():
    trades = [create_trade("T001", "USD"), create_trade("T002", "USD")]
    results = [
        create_priced_option("T001", 1000.0, 0.4, 0.002),
        create_priced_option("T002", 2000.0, 0.5, 0.003),
    ]
    summaries = aggregate_by_currency(trades, results)
    usd = next(s for s in summaries if s.notional_ccy == "USD")

    expected_pv = 3000.0
    expected_delta = 0.9
    expected_vega = 0.005

    assert usd.total_pv == pytest.approx(expected_pv, DIFF_TOLERANCE)
    assert usd.total_delta == pytest.approx(expected_delta, DIFF_TOLERANCE)
    assert usd.total_vega == pytest.approx(expected_vega, DIFF_TOLERANCE)


def test_single_currency_produces_one_summary():
    trades = [create_trade("T001", "USD")]
    results = [create_priced_option("T001", 1000.0, 0.4, 0.002)]
    summaries = aggregate_by_currency(trades, results)
    assert len(summaries) == 1
    assert summaries[0].notional_ccy == "USD"


def test_empty_trades_returns_empty_summaries():
    summaries = aggregate_by_currency([], [])
    assert summaries == []