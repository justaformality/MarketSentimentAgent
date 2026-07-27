import pandas as pd
import pytest

from technical_indicators import (
    add_all_indicators,
    add_macd,
    add_moving_averages,
    add_rsi,
    technical_summary,
)


def make_prices(values):
    return pd.DataFrame(
        {
            "Close": values
        }
    )


def test_add_moving_averages():
    data = make_prices(
        range(1, 61)
    )

    result = add_moving_averages(
        data.copy()
    )

    # A 20-day SMA should not exist before
    # there are 20 observations.
    assert pd.isna(
        result.loc[18, "SMA_20"]
    )

    expected_sma_20 = (
        sum(range(1, 21)) / 20
    )

    assert result.loc[
        19,
        "SMA_20",
    ] == pytest.approx(
        expected_sma_20
    )

    # Same check for SMA 50.
    assert pd.isna(
        result.loc[48, "SMA_50"]
    )

    expected_sma_50 = (
        sum(range(1, 51)) / 50
    )

    assert result.loc[
        49,
        "SMA_50",
    ] == pytest.approx(
        expected_sma_50
    )


def test_rsi_for_continuously_rising_prices():
    data = make_prices(
        range(1, 30)
    )

    result = add_rsi(
        data.copy(),
        period=14,
    )

    assert result["RSI"].iloc[-1] \
        == pytest.approx(100.0)


def test_rsi_for_continuously_falling_prices():
    data = make_prices(
        range(30, 1, -1)
    )

    result = add_rsi(
        data.copy(),
        period=14,
    )

    assert result["RSI"].iloc[-1] \
        == pytest.approx(0.0)


def test_macd_matches_expected_ema_calculation():
    data = make_prices(
        [
            10,
            11,
            12,
            13,
            14,
            15,
            14,
            16,
            17,
            18,
        ]
    )

    result = add_macd(
        data.copy()
    )

    ema_12 = (
        data["Close"]
        .ewm(
            span=12,
            adjust=False,
        )
        .mean()
    )

    ema_26 = (
        data["Close"]
        .ewm(
            span=26,
            adjust=False,
        )
        .mean()
    )

    expected_macd = (
        ema_12 - ema_26
    )

    expected_signal = (
        expected_macd
        .ewm(
            span=9,
            adjust=False,
        )
        .mean()
    )

    pd.testing.assert_series_equal(
        result["MACD"],
        expected_macd,
        check_names=False,
    )

    pd.testing.assert_series_equal(
        result["Signal_Line"],
        expected_signal,
        check_names=False,
    )


def test_add_all_indicators():
    data = make_prices(
        range(1, 80)
    )

    result = add_all_indicators(
        data.copy()
    )

    expected_columns = [
        "SMA_20",
        "SMA_50",
        "RSI",
        "MACD",
        "Signal_Line",
    ]

    for column in expected_columns:
        assert column in result.columns


def test_technical_summary_bullish():
    data = pd.DataFrame(
        [
            {
                "Close": 110.0,
                "SMA_20": 100.0,
                "SMA_50": 95.0,
                "RSI": 55.0,
                "MACD": 2.0,
                "Signal_Line": 1.0,
            }
        ]
    )

    result = technical_summary(data)

    assert result == [
        "Price is above the 20-day moving average.",
        "Price is above the 50-day moving average.",
        "RSI is in a neutral range.",
        "MACD is bullish.",
    ]


def test_technical_summary_bearish_overbought():
    data = pd.DataFrame(
        [
            {
                "Close": 90.0,
                "SMA_20": 100.0,
                "SMA_50": 105.0,
                "RSI": 75.0,
                "MACD": -1.0,
                "Signal_Line": 0.0,
            }
        ]
    )

    result = technical_summary(data)

    assert result == [
        "Price is below the 20-day moving average.",
        "Price is below the 50-day moving average.",
        "RSI suggests the stock may be overbought.",
        "MACD is bearish.",
    ]