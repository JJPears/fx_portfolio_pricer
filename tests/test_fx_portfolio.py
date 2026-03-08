import pytest
from src.portfolio.fx_portfolio import FXPortfolio


def test_price_trades_raises_if_no_trades_loaded():
    portfolio = FXPortfolio()
    with pytest.raises(RuntimeError, match="No trades loaded"):
        portfolio.price_trades()


def test_build_portfolios_raises_if_no_priced_options():
    portfolio = FXPortfolio()
    portfolio._trades = ["dummy"]  # type: ignore
    with pytest.raises(RuntimeError, match="No priced options"):
        portfolio.build_portfolios()


def test_write_raises_if_no_summaries(tmp_path):
    portfolio = FXPortfolio()
    portfolio._priced_options = ["dummy"]  # type: ignore
    with pytest.raises(RuntimeError, match="No summaries built"):
        portfolio.write(str(tmp_path / "output.xlsx"))
