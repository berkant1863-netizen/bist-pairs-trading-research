BIST Pairs Trading | Quantitative Research

In this project, I explored a pairs trading strategy using 12 stocks listed on Borsa Istanbul. My goal was to investigate whether statistical relationships between stocks could be turned into a profitable trading strategy after accounting for transaction costs.

Using Python, I selected stock pairs based on correlation and cointegration tests, estimated dynamic hedge ratios with rolling OLS regression, and generated trading signals using a z score based mean reversion approach. To evaluate the strategy, I built a walk-forward backtesting framework covering 22 periods and 1,386 out-of-sample trading days.

The strategy produced a total return of 3.04% before transaction costs. However, after applying a 0.10% transaction cost to traded notional, the return dropped to −3.75%. This comparison helped me understand how significantly trading costs can affect the performance of a statistical trading strategy.

Throughout the project, I focused not only on developing the strategy but also on evaluating its results and understanding its limitations. One of my key takeaways was that identifying statistically related stocks does not necessarily translate into a profitable trading strategy.

I developed the project using Python, pandas, NumPy, statsmodels, and yfinance. It is intended as a quantitative research prototype rather than a live trading system, and it does not fully account for real-world execution conditions or short-selling costs.
