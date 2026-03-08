from models.models import FXOptionTrade, PricedOption, PortfolioSummary
from common.reader import load_fx_options_trades
from pricing.black_scholes import price_fx_option
from portfolio_aggregator.aggregator import aggregate_by_currency
from common.writer import write_output
import logging

logger = logging.getLogger(__name__)


class FXPortfolio:
    """Central object holding state for trades including pricing and aggregations for portfolio report generation"""

    def __init__(self) -> None:
        self._trades: list[FXOptionTrade] = []
        self._priced_options: list[PricedOption] = []
        self._summaries: list[PortfolioSummary] = []

    def load_trades(self, input_path: str) -> None:
        self._trades = load_fx_options_trades(input_path)

    def price_trades(self) -> None:

        if not self._trades:
            raise RuntimeError("No trades loaded — call load_trades() first")

        self._priced_options = [
            price_fx_option(
                trade_id=trade.trade_id,
                spot=trade.spot,
                strike=trade.strike,
                vol=trade.vol,
                rate_dom=trade.rate_dom,
                rate_foreign=trade.rate_foreign,
                expiry=trade.expiry,
                notional=trade.notional,
                option_type=trade.option_type,
            )
            for trade in self._trades
        ]

    def build_portfolios(self) -> None:
        if not self._priced_options:
            raise RuntimeError("No priced options — call price_trades() first")
        self._summaries = aggregate_by_currency(self._trades, self._priced_options)

    def write(self, output_path: str) -> None:
        if not self._summaries:
            raise RuntimeError("No summaries built — call build_portfolios() first")
        write_output(output_path, self._trades, self._priced_options, self._summaries)

    def generate_fx_portfolio(self, input_file: str, output_path: str) -> None:
        self.load_trades(input_file)
        self.price_trades()
        self.build_portfolios()
        self.write(output_path)
        logger.info(
            "FX portfolio report generated successfully: summary and trades written to %s",
            output_path,
        )
