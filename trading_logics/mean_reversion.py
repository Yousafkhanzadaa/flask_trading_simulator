import pandas as pd
def simulate_mean_reversion_trading(data, initial_balance, buy_threshold, sell_threshold, lookback_window):
    balance = initial_balance
    units_held = 0
    balance_history = []
    trade_actions = []

    # Calculate the moving average using a rolling window
    data['Moving_Average'] = data['Close'].rolling(window=lookback_window).mean()

    # Iterate over the historical price data to simulate trades
    for index, row in data.iterrows():
        current_price = row['Close']
        moving_average = row['Moving_Average']
        # print(current_price <= moving_average * (1 - buy_threshold))
        if pd.isna(moving_average):
            continue  # Skip if the moving average is not available (beginning of the dataset)

        # BUY logic: current price is lower than the moving average by buy_threshold
        if balance > 0 and current_price <= moving_average * (1 - buy_threshold):
            units_to_buy = balance / current_price  # Use all balance to buy
            units_held += units_to_buy
            balance = 0
            trade_actions.append({'date': index, 'action': 'buy', 'price': current_price, 'units': units_to_buy})
            # print("BUY")

        # SELL logic: current price is higher than the moving average by sell_threshold
        elif units_held > 0 and current_price >= moving_average * (1 + sell_threshold):
            balance += units_held * current_price  # Sell all units held
            units_held = 0
            trade_actions.append({'date': index, 'action': 'sell', 'price': current_price, 'units': 0})
            # print("Sell")


        balance_history.append({'Date': index, 'Balance': balance + (units_held * current_price)})
    final_balance = balance + (units_held * current_price)

    return balance_history, trade_actions, final_balance