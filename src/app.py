#!/usr/bin/env python3

from portfolio.fx_portfolio import FXPortfolio
import argparse
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="FX Options Portfolio Risk Aggregator")
    parser.add_argument("--input", required=True, help="Path to input xlsx file")
    parser.add_argument("--output", required=True, help="Path to output xlsx file")
    args = parser.parse_args()

    fx_portfolio = FXPortfolio()
    fx_portfolio.generate_fx_portfolio(args.input, args.output)
