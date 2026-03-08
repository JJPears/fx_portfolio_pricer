import os
import pandas as pd
import pytest
from src.portfolio.fx_portfolio import FXPortfolio

INPUT_PATH = os.path.join(os.path.dirname(__file__), "data/fx_trades__1_.xlsx")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "data/output.xlsx")


@pytest.fixture(autouse=True)
def cleanup():
    yield
    if os.path.exists(OUTPUT_PATH):
        os.remove(OUTPUT_PATH)


def test_full_pipeline_produces_output():
    portfolio = FXPortfolio()
    portfolio.generate_fx_portfolio(INPUT_PATH, OUTPUT_PATH)
    assert os.path.exists(OUTPUT_PATH)


def test_output_has_correct_sheets():
    portfolio = FXPortfolio()
    portfolio.generate_fx_portfolio(INPUT_PATH, OUTPUT_PATH)
    output = pd.ExcelFile(OUTPUT_PATH, engine="calamine")
    assert "Summary" in output.sheet_names
    assert "Trades" in output.sheet_names


def test_trades_sheet_has_correct_columns():
    portfolio = FXPortfolio()
    portfolio.generate_fx_portfolio(INPUT_PATH, OUTPUT_PATH)
    df = pd.read_excel(OUTPUT_PATH, sheet_name="Trades", engine="calamine")
    assert set(df.columns) == {"trade_id", "notional_ccy", "pv", "delta", "vega", "itm"}


def test_summary_sheet_has_correct_columns():
    portfolio = FXPortfolio()
    portfolio.generate_fx_portfolio(INPUT_PATH, OUTPUT_PATH)
    df = pd.read_excel(OUTPUT_PATH, sheet_name="Summary", engine="calamine")
    assert set(df.columns) == {"notional_ccy", "total_pv", "total_delta", "total_vega"}


def test_all_trades_priced():
    portfolio = FXPortfolio()
    portfolio.generate_fx_portfolio(INPUT_PATH, OUTPUT_PATH)
    df = pd.read_excel(OUTPUT_PATH, sheet_name="Trades", engine="calamine")
    trade_count = 10
    assert len(df) == trade_count
    assert df["pv"].notna().all()
    assert df["delta"].notna().all()
    assert df["vega"].notna().all()


def test_pv_always_positive():
    portfolio = FXPortfolio()
    portfolio.generate_fx_portfolio(INPUT_PATH, OUTPUT_PATH)
    df = pd.read_excel(OUTPUT_PATH, sheet_name="Trades", engine="calamine")
    assert (df["pv"] >= 0).all()


def test_summary_groups_by_currency():
    portfolio = FXPortfolio()
    portfolio.generate_fx_portfolio(INPUT_PATH, OUTPUT_PATH)
    df = pd.read_excel(OUTPUT_PATH, sheet_name="Summary", engine="calamine")
    assert set(df["notional_ccy"]) == {"USD", "JPY"}