import numpy as np
from scipy.stats import norm
from common.enums import OptionType
from models.models import PricedOption


def price_fx_option(
    trade_id: str,
    spot: float,
    strike: float,
    vol: float,
    rate_dom: float,
    rate_foreign: float,
    expiry: float,
    notional: float,
    option_type: OptionType,
) -> PricedOption:
    """
    Garman-Kohlhagen FX option pricer, assumes data has been pre validated
    """

    d1, d2 = _calculate_d1_d2(spot, strike, vol, rate_dom, rate_foreign, expiry)

    df_dom = np.exp(-rate_dom * expiry)
    df_foreign = np.exp(-rate_foreign * expiry)

    if option_type == OptionType.CALL:
        price = spot * df_foreign * norm.cdf(d1) - strike * df_dom * norm.cdf(d2)
        pv = round(notional * price, 2)
        delta = df_foreign * norm.cdf(d1)
        itm = spot > strike
    else:
        price = strike * df_dom * norm.cdf(-d2) - spot * df_foreign * norm.cdf(-d1)
        pv = round(notional * price, 2)
        delta = df_foreign * (norm.cdf(d1) - 1)
        itm = spot < strike

    vega = (spot * df_foreign * norm.pdf(d1) * np.sqrt(expiry)) / 100

    return PricedOption(trade_id=trade_id, pv=pv, delta=delta, vega=vega, itm=itm)


def _calculate_d1_d2(
    spot: float,
    strike: float,
    vol: float,
    rate_dom: float,
    rate_foreign: float,
    expiry: float,
) -> tuple[float, float]:

    sqrt_t = np.sqrt(expiry)
    d1 = (np.log(spot / strike) + (rate_dom - rate_foreign + vol**2 * 0.5) * expiry) / (
        vol * sqrt_t
    )
    d2 = d1 - (vol * sqrt_t)
    return d1, d2
