# BIST Statistical Arbitrage: Pairs Trading Research

### Cointegration, Mean Reversion & Walk-Forward Backtesting

## Overview

This project investigates statistical arbitrage opportunities among equities listed on Borsa Istanbul (BIST) using pairs trading and mean-reversion techniques.

The objective is to identify statistically related equity pairs, construct market-relative trading signals, and evaluate their performance using out-of-sample walk-forward backtesting.

**Research Question:** Can cointegration-based pairs trading strategies generate positive risk-adjusted returns after transaction costs?

## Methodology

### 1. Data Collection

Historical adjusted equity prices are retrieved using Python and the `yfinance` library.

The research considers an initial universe of 30 BIST equities, subject to data availability and quality filters.

### 2. Pair Selection

Candidate pairs are evaluated using:

- Daily return correlation
- Engle-Granger cointegration tests
- Ordinary Least Squares (OLS) regression
- Estimated spread mean-reversion half-life

Pairs are selected using the historical formation period, without using subsequent trading-window prices for selection.

### 3. Walk-Forward Framework

The strategy uses:

| Parameter | Value |
|---|---:|
| Formation window | 252 trading days |
| Out-of-sample trading window | 63 trading days |
| Maximum pairs per window | 5 |
| Rolling hedge ratio window | 60 days |
| Rolling Z-score window | 20 days |

The formation and trading windows advance sequentially through the historical dataset.

### 4. Trading Strategy

Trading signals are based on the standardized spread (Z-score).

| Rule | Threshold |
|---|---:|
| Long-spread entry | Z-score ≤ -2.0 |
| Short-spread entry | Z-score ≥ +2.0 |
| Exit | Absolute Z-score ≤ 0.5 |
| Stop condition | Absolute Z-score ≥ 3.5 in the adverse direction |

The strategy estimates rolling hedge ratios and shifts signal calculations to reduce look-ahead bias.

### 5. Transaction Costs

The backtest applies an assumed round-trip transaction cost of 10 basis points.

Both gross and net returns are evaluated.

This is a simplified cost model and does not fully account for financing, borrow availability, execution slippage, or market impact.

## Research Outputs

The repository includes:

- `pairs_trading.py`: Research and backtesting implementation.
- `pairs_selected_walkforward.csv`: Selected pairs and their formation-window statistics.
- `pairs_oos_daily_returns.csv`: Simulated out-of-sample daily portfolio return observations.

The strategy calculates cumulative returns, annualized Sharpe ratio, volatility, maximum drawdown, and positive-day frequency.

## Limitations

- Pair relationships and cointegration may break down over time.
- Transaction costs are simplified assumptions.
- Short-selling constraints and borrowing costs are not fully modeled.
- Historical stock-universe selection may introduce survivorship bias.
- Windows without eligible pairs require careful treatment when evaluating calendar-time portfolio performance.
- Open positions at the boundaries of trading windows require additional execution and accounting validation.

Reported results should be interpreted as exploratory simulated performance, not verified live-trading returns.

## Conclusion

The project demonstrates the development of a systematic statistical arbitrage research framework combining econometric pair selection, mean-reversion signals, rolling parameter estimation, and walk-forward evaluation.

Further research should focus on execution realism, robust portfolio accounting, and validation across different market regimes.

## Technology

Python, Pandas, NumPy, Statsmodels, yfinance.

## Disclaimer

This project is intended for educational and quantitative research purposes only. It does not constitute investment advice or a live-trading recommendation.
