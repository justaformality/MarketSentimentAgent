import pandas as pd


def add_moving_averages(data: pd.DataFrame):
    data["SMA_20"] = data["Close"].rolling(window=20).mean()
    data["SMA_50"] = data["Close"].rolling(window=50).mean()
    return data


def add_rsi(data: pd.DataFrame, period: int = 14):
    delta = data["Close"].diff()

    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    data["RSI"] = 100 - (100 / (1 + rs))

    return data


def add_macd(data: pd.DataFrame):
    ema_12 = data["Close"].ewm(span=12, adjust=False).mean()
    ema_26 = data["Close"].ewm(span=26, adjust=False).mean()

    data["MACD"] = ema_12 - ema_26
    data["Signal_Line"] = data["MACD"].ewm(span=9, adjust=False).mean()

    return data


def add_all_indicators(data: pd.DataFrame):
    data = add_moving_averages(data)
    data = add_rsi(data)
    data = add_macd(data)
    return data


def technical_summary(data: pd.DataFrame):
    latest = data.iloc[-1]

    close = latest["Close"]
    sma_20 = latest["SMA_20"]
    sma_50 = latest["SMA_50"]
    rsi = latest["RSI"]
    macd = latest["MACD"]
    signal_line = latest["Signal_Line"]

    signals = []

    if pd.notna(sma_20) and close > sma_20:
        signals.append("Price is above the 20-day moving average.")
    elif pd.notna(sma_20):
        signals.append("Price is below the 20-day moving average.")

    if pd.notna(sma_50) and close > sma_50:
        signals.append("Price is above the 50-day moving average.")
    elif pd.notna(sma_50):
        signals.append("Price is below the 50-day moving average.")

    if pd.notna(rsi):
        if rsi > 70:
            signals.append("RSI suggests the stock may be overbought.")
        elif rsi < 30:
            signals.append("RSI suggests the stock may be oversold.")
        else:
            signals.append("RSI is in a neutral range.")

    if pd.notna(macd) and pd.notna(signal_line):
        if macd > signal_line:
            signals.append("MACD is bullish.")
        else:
            signals.append("MACD is bearish.")

    return signals