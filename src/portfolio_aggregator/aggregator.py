from models.models import PortfolioSummary, FXOptionTrade, PricedOption


def aggregate_by_currency(
    trades: list[FXOptionTrade], priced_options: list[PricedOption]
) -> list[PortfolioSummary]:
    """Aggregates priced options by notional currency, returning one PortfolioSummary per currency."""
    trade_ccy_map = {trade.trade_id: trade.notional_ccy for trade in trades}

    buckets: dict[str, list[PricedOption]] = {}

    for option in priced_options:
        ccy = trade_ccy_map[option.trade_id]
        buckets.setdefault(ccy, []).append(option)

    return [
        PortfolioSummary(
            notional_ccy=ccy,
            total_pv=round(sum(r.pv for r in bucket), 2),
            total_delta=round(sum(r.delta for r in bucket), 4),
            total_vega=round(sum(r.vega for r in bucket), 4),
        )
        for ccy, bucket in buckets.items()
    ]
