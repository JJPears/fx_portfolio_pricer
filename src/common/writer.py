import pandas as pd
from models.models import FXOptionTrade, PricedOption, PortfolioSummary


def write_output(
    output_path: str,
    trades: list[FXOptionTrade],
    priced_options: list[PricedOption],
    summaries: list[PortfolioSummary],
) -> None:
    trade_ccy_map = {t.trade_id: t.notional_ccy for t in trades}

    trades_df = pd.DataFrame(
        [
            {
                "trade_id": option.trade_id,
                "notional_ccy": trade_ccy_map[option.trade_id],
                "pv": option.pv,
                "delta": option.delta,
                "vega": option.vega,
                "itm": option.itm,
            }
            for option in priced_options
        ]
    )
    trades_df = trades_df.sort_values("notional_ccy")

    summary_df = pd.DataFrame(
        [
            {
                "notional_ccy": summary.notional_ccy,
                "total_pv": summary.total_pv,
                "total_delta": summary.total_delta,
                "total_vega": summary.total_vega,
            }
            for summary in summaries
        ]
    )

    with pd.ExcelWriter(output_path) as writer:
        summary_df.to_excel(writer, sheet_name="Summary", index=False)
        trades_df.to_excel(writer, sheet_name="Trades", index=False)
