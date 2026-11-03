import pandas as pd
import numpy as np
import yfinance as yf 
from statsmodels.tsa.stattools import coint
import statsmodels.api as sm

START_DATE = "2020-01-01"
END_DATE = "2026-10-01"

FORMATION_DAYS = 252
TRADING_DAYS = 63

MIN_CORRELATION = 0.60
MAX_COINTEGRATION_PVALUE = 0.05

TICKERS = [
    "AKBNK.IS",
    "GARAN.IS",
    "ISCTR.IS",
    "KCHOL.IS",
    "THYAO.IS",
    "TUPRS.IS",
    "BIMAS.IS",
    "EREGL.IS",
    "FROTO.IS",
    "SAHOL.IS",
    "SISE.IS",
    "TCELL.IS"
]

def download_prices():
    downloaded = yf.download(
        tickers = TICKERS,
        start = START_DATE,
        end = END_DATE,
        auto_adjust = True,
        progress=False
    )

    df = downloaded["Close"].copy()

    return df

df = download_prices()

def validate_prices(df):
    missing_price_data = df.isna().sum().sum()
    zero_negative_price_data = (df <= 0).sum().sum()

    if missing_price_data + zero_negative_price_data > 0:
        raise ValueError("Invalid price data")
    else:
        print("Valid price data")

        return df

# price_data_validation = validate_prices(df)
# print(price_data_validation)

print("before_cleaning:", df.shape)

df = df.dropna()

print("after_cleaning:", df.shape)

df = validate_prices(df)
print(df.head())

def create_walkforward_windows(df, formation_days, trading_days):
    windows = []

    for i in range(0, len(df) - trading_days + 1, trading_days):
        start_formation_days = i
        end_formation_days = i + FORMATION_DAYS
        start_trading_days = i + FORMATION_DAYS
        end_trading_days = i + FORMATION_DAYS + TRADING_DAYS

        formation_prices = df.iloc[start_formation_days:end_formation_days]
        trading_prices = df.iloc[start_trading_days:end_trading_days]

        if len(formation_prices) != formation_days or len(trading_prices) != trading_days:
            continue

    

        windows.append({"formation": formation_prices,
                       "trading": trading_prices})

    return windows

result = create_walkforward_windows(df,formation_days = FORMATION_DAYS,
                                trading_days = TRADING_DAYS)

# print("Total valid windows:", len(result))

# print("First formation:", result[0]["formation"].shape)
# print("First OOS:", result[0]["trading"].shape)

# print("Latest formation:", result[-1]["formation"].shape)
# print("Latest OOS:", result[-1]["trading"].shape)

def select_pairs(formation_prices, min_corr, max_pvalue):
    formation_return = formation_prices.pct_change(fill_method=None).dropna()
    corr_matrix = formation_return.corr()
    pair_candidates = []
    symbols = list(corr_matrix.columns)
    formation_log_prices = np.log(formation_prices)
    cointegrated_pairs = []

    for j in range(len(symbols)):
        stock_a = symbols[j]
        for  x in range(j + 1, len(symbols)):
            stock_b = symbols[x]

            corr = corr_matrix.loc[stock_a, stock_b]
            if corr >= min_corr:
                pair_candidates.append([stock_a,stock_b,corr])

    for pair in pair_candidates:
        stock_a = pair[0]
        stock_b = pair[1]
        stock_a_log_price = formation_log_prices[stock_a]
        stock_b_log_price = formation_log_prices[stock_b]
        cointegration = coint(stock_a_log_price,
                                    stock_b_log_price
                                    )
        if cointegration[1] <= max_pvalue:
            cointegrated_pairs.append([stock_a,
                                        stock_b,
                                        pair[2],
                                        cointegration[1]]
                                        )
    return cointegrated_pairs



for window in result:

    selected_pairs = select_pairs(
        window["formation"],
        MIN_CORRELATION,
        MAX_COINTEGRATION_PVALUE
    )

    window["selected_pairs"] = selected_pairs

    print(selected_pairs[:5])
    print("Number of candidate pairs:", len(selected_pairs))

def calculate_rolling_hedge(formation_prices, trading_prices,stock_a,stock_b, window=60):

    df = pd.concat([formation_prices, trading_prices])
    df = df[[stock_a, stock_b]]
    log_prices = np.log(df)
    dates_alpha_beta = []

    for t in range(window, len(log_prices)):
        historical_prices = log_prices.iloc[t-window:t]
        y = historical_prices[stock_a]
        X = historical_prices[stock_b]
        constant = sm.add_constant(X)
        model = sm.OLS(y, constant).fit()
        beta = model.params[stock_b]
        alpha = model.params["const"]
        dates_alpha_beta.append([log_prices.index[t], alpha, beta])
    dates_alpha_beta_df = pd.DataFrame(dates_alpha_beta, columns=[
        "DATES", "ALPHA", "BETA"
    ])
                                                                  
    dates_alpha_beta_df = dates_alpha_beta_df.set_index("DATES")


    dates_alpha_beta_df["SPREAD"] = (
    log_prices[stock_a]
    - dates_alpha_beta_df["ALPHA"]
    - dates_alpha_beta_df["BETA"] * log_prices[stock_b]
)
    dates_alpha_beta_df["ROLLİNG_MEAN"] = dates_alpha_beta_df["SPREAD"].rolling(20).mean()
    dates_alpha_beta_df["ROLLİNG_STD"] = dates_alpha_beta_df["SPREAD"].rolling(20).std()
    dates_alpha_beta_df["ZSCORE"] = ((dates_alpha_beta_df["SPREAD"]
    - dates_alpha_beta_df["ROLLİNG_MEAN"])
    / dates_alpha_beta_df["ROLLİNG_STD"])
    return dates_alpha_beta_df

for window in result:
    hedge_results = {}

    for pair in window["selected_pairs"]:
        stock_a = pair[0]
        stock_b = pair[1]
        hedge_df = calculate_rolling_hedge(
            window["formation"],
            window["trading"],
            stock_a,
            stock_b,
            window=60
        )

        hedge_results[(stock_a, stock_b)] = hedge_df
    window["hedge_results"] = hedge_results

for window in result:
    print(
        "Selected pair:", len(window["selected_pairs"]),
        "Calculated pair:", len(window["hedge_results"])
    )

def generate_signals(hedge_df, entry_z=2.0, exit_z=0.5, stop_z=3.5):
    positions = []
    current_position = 0

    oos_zscores = hedge_df["ZSCORE"].tail(TRADING_DAYS)

    for z in oos_zscores:
        if current_position == 0:

            if entry_z <= z < stop_z:
                current_position = - 1

            elif -stop_z < z <= -entry_z:
                current_position = 1

        elif current_position == 1:

            if z >= -exit_z or z <= -stop_z:
                current_position = 0

        elif current_position == -1:

            if z <= exit_z or z >= stop_z:
                current_position = 0

        positions.append(current_position)

    return pd.Series(
        positions,
        index=oos_zscores.index,
        name="TARGET_POSITION"
    )

for window in result:

    signal_results = {}

    for pair, hedge_df in window["hedge_results"].items():

        signal_results[pair] = generate_signals(hedge_df)

    window["signal_results"] = signal_results

def backtest_pair(hedge_df, target_positions, trading_prices, stock_a, stock_b, cost_rate=0.001):

    oos_prices = trading_prices[[stock_a, stock_b]]
    oos_returns = oos_prices.pct_change(fill_method=None)

    executed_positions = target_positions.shift(1).fillna(0)
    held_positions = executed_positions.shift(1).fillna(0)

    executed_positions.iloc[-1] = 0
    execution_beta = hedge_df["BETA"].reindex(oos_prices.index).shift(1)

    gross = 1 + execution_beta.abs()

    target_weight_a = (executed_positions / gross).fillna(0.0)

    target_weight_b = (
        -executed_positions * execution_beta / gross
    ).fillna(0.0)

    cash = 1.0
    qty_a = 0.0
    qty_b = 0.0

    daily_results = []
    cost_rate = 0.001

    for date in oos_prices.index:

        price_a = oos_prices.loc[date, stock_a]
        price_b = oos_prices.loc[date, stock_b]

        equity_before_trade = (
            cash
            + qty_a * price_a
            + qty_b * price_b
        )
        weight_a = target_weight_a.loc[date]
        weight_b = target_weight_b.loc[date]

        target_qty_a = equity_before_trade * weight_a / price_a
        target_qty_b = equity_before_trade * weight_b / price_b
        trade_a = target_qty_a - qty_a
        trade_b = target_qty_b - qty_b

        trade_value_a = trade_a * price_a
        trade_value_b = trade_b * price_b

        transaction_cost = cost_rate * (
            abs(trade_value_a) + abs(trade_value_b)
        )
        cash = cash - trade_value_a - trade_value_b - transaction_cost

        qty_a = target_qty_a
        qty_b = target_qty_b

        equity_after_trade = (
            cash
            + qty_a * price_a
            + qty_b * price_b
        )

        daily_results.append({
            "DATE": date,
            "EQUITY": equity_after_trade,
            "TRANSACTION_COST": transaction_cost,
            "CASH": cash,
            "QTY_A": qty_a,
            "QTY_B": qty_b

        })
    backtest_df = pd.DataFrame(daily_results)
    backtest_df = backtest_df.set_index("DATE")
    backtest_df["DAILY_RETURN"] = (
        backtest_df["EQUITY"]
        .pct_change(fill_method=None)
        .fillna(0.0)
    )
    return backtest_df



for window in result:

    backtest_results = {}

    for pair, hedge_df in window["hedge_results"].items():

        stock_a = pair[0]
        stock_b = pair[1]

        target_positions = window["signal_results"][pair]

        backtest_df = backtest_pair(
            hedge_df,
            target_positions,
            window["trading"],
            stock_a,
            stock_b
        )

        backtest_results[pair] = backtest_df

    window["backtest_results"] = backtest_results

portfolio_returns = []

for window in result:

    pair_backtests = window["backtest_results"]

    if pair_backtests:

        pair_equities = pd.concat(
            [bt["EQUITY"] for bt in pair_backtests.values()],
            axis=1
        )

        window_equity = pair_equities.mean(axis=1)

    else:

        window_equity = pd.Series(
            1.0,
            index=window["trading"].index
        )

    window_returns = (
        window_equity / window_equity.shift(1).fillna(1.0)
    ) - 1.0

    window["portfolio_returns"] = window_returns

    portfolio_returns.append(window_returns)

all_returns = pd.concat(portfolio_returns).sort_index()
equity_curve = (1 + all_returns).cumprod()

total_return = equity_curve.iloc[-1] - 1

print("Total number of oos days:", len(all_returns))
print("Finla portfolio value:", equity_curve.iloc[-1])
print(f"Total net return: %{total_return * 100:.2f}")

for i, window in enumerate(result, start=1):

    for pair, bt in window["backtest_results"].items():

        if (bt["EQUITY"] <= 0).any():

            print("Problematic period:", i)
            print("Problematic pair:", pair)

            print(bt.loc[bt["EQUITY"] <= 0].head())

            break

sharpe = (
    np.sqrt(252) * all_returns.mean()
    / all_returns.std()
)

drawdown = equity_curve / equity_curve.cummax() - 1

max_drawdown = drawdown.min()

print(f"Sharpe Ratio: {sharpe:.3f}")
print(f"Maximum Drawdown: %{max_drawdown * 100:.2f}")

window_costs = []

for window in result:

    backtests = window["backtest_results"]

    if backtests:
        total_cost = sum(
            bt["TRANSACTION_COST"].sum()
            for bt in backtests.values()
        )

        window_cost = total_cost / len(backtests)

    else:
        window_cost = 0.0

    window_costs.append(window_cost)

print("Total weighted cost:", sum(window_costs))
print("Peirod with the highest cost:", np.argmax(window_costs) + 1)
print("Cost of that period:", max(window_costs))

    

