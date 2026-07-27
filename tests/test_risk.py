import pytest

from risk import risk_matrix


@pytest.mark.parametrize(
    ("sentiment", "price_change", "expected"),
    [
        (
            0.30,
            -2.01,
            "Divergence Alert: Positive news, but price is falling.",
        ),
        (
            -0.30,
            2.01,
            "Divergence Alert: Negative news, but price is rising.",
        ),
        (
            0.30,
            2.01,
            "Bullish Confirmation: Positive news and price rising.",
        ),
        (
            -0.30,
            -2.01,
            "Bearish Confirmation: Negative news and price falling.",
        ),

        # Neutral cases
        (
            0.29,
            10,
            "Neutral / No strong signal.",
        ),
        (
            0.80,
            2.0,
            "Neutral / No strong signal.",
        ),
        (
            -0.80,
            -2.0,
            "Neutral / No strong signal.",
        ),
        (
            0.0,
            0.0,
            "Neutral / No strong signal.",
        ),
    ],
)
def test_risk_matrix(sentiment, price_change, expected):
    result = risk_matrix(
        avg_sentiment=sentiment,
        price_change=price_change,
    )

    assert result == expected