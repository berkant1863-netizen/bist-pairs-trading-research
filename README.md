BIST Statistical Arbitrage and Pairs Trading Research

This project investigates statistical arbitrage opportunities in Borsa Istanbul (BIST) equities using cointegration based pairs trading strategies and walk forward backtesting.

Historical price data for 30 BIST stocks was collected using Python and Yahoo Finance. Potential trading pairs were identified through return correlation analysis, Engle Granger cointegration tests, and mean reversion half life estimation. Rolling hedge ratios and Z scores were then used to generate systematic entry and exit signals.

The strategy was evaluated using a walk forward backtesting framework consisting of 252 day formation periods and 63 day out of sample trading windows. Transaction costs were incorporated into the calculations, and strategy performance was analyzed using metrics such as cumulative returns, the Sharpe ratio, annualized volatility, and maximum drawdown.

The research examines whether stock pairs that have historically exhibited cointegration can generate profitable trading opportunities through mean reversion outside the formation period. The study also highlights the importance of transaction costs, changing relationships between stock pairs, and proper backtesting methodology.

This Quantitative Research project focuses on statistical arbitrage, time series analysis, systematic trading strategies, and out of sample performance evaluation.
