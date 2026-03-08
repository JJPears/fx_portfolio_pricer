import logging
import pandas as pd
from models.models import FXOptionTrade

logger = logging.getLogger(__name__)


def load_fx_options_trades(
    file_path: str, header: int = 0, sheet_name: str | int = 0
) -> list[FXOptionTrade]:
    """
    Loads FX option trades from an xlsx file.
    Returns a tuple of (valid_trades, invalid_rows).
    Invalid rows will alert with a warning log and be captured with their error.
    """
    df = pd.read_excel(
        file_path, header=header, sheet_name=sheet_name, engine="calamine"
    )

    if df.empty:
        raise ValueError(f"No data in file: {file_path}")

    df = df.rename(
        columns={
            "TradeID": "trade_id",
            "Underlying": "underlying",
            "Notional": "notional",
            "NotionalCurrency": "notional_ccy",
            "Spot": "spot",
            "Strike": "strike",
            "Vol": "vol",
            "RateDomestic": "rate_dom",
            "RateForeign": "rate_foreign",
            "Expiry": "expiry",
            "OptionType": "option_type",
        }
    )
    return _parse_options_trades(df)


def _parse_options_trades(df: pd.DataFrame) -> list[FXOptionTrade]:
    valid_trades = []

    for record in df.to_dict("records"):
        try:
            normalised_record = {str(k): v for k, v in record.items()}
            valid_trades.append(FXOptionTrade(**normalised_record))
        except Exception as e:
            logger.warning(
                "Failed to parse trade %s: %s", record.get("trade_id", "UNKNOWN"), e
            )

    return valid_trades
