def risk_matrix(avg_sentiment, price_change):
    if avg_sentiment >= 0.3 and price_change < -2:
        return "Divergence Alert: Positive news, but price is falling."

    if avg_sentiment <= -0.3 and price_change > 2:
        return "Divergence Alert: Negative news, but price is rising."

    if avg_sentiment >= 0.3 and price_change > 2:
        return "Bullish Confirmation: Positive news and price rising."

    if avg_sentiment <= -0.3 and price_change < -2:
        return "Bearish Confirmation: Negative news and price falling."

    return "Neutral / No strong signal."