from types import SimpleNamespace
from unittest.mock import patch

from llm_summary import (
    generate_market_summary,
)


def test_generate_market_summary():
    articles = [
        {
            "title": f"Headline {i}",
            "source": "Example",
            "sentiment_label":
                "Positive",
            "sentiment_score":
                0.5,
            "description":
                f"Description {i}",
        }
        for i in range(8)
    ]

    fake_response = SimpleNamespace(
        output_text=(
            "Generated beginner summary"
        )
    )

    with patch(
        "llm_summary.client.responses.create",
        return_value=fake_response,
    ) as create_mock:

        result = generate_market_summary(
            ticker="AAPL",
            company_name="Apple",
            price_change=5.2,
            avg_sentiment=0.4,
            signal=(
                "Bullish Confirmation"
            ),
            technical_signals=[
                "MACD is bullish.",
                "RSI is neutral.",
            ],
            articles=articles,
        )

    assert result \
        == "Generated beginner summary"

    create_mock.assert_called_once()

    kwargs = (
        create_mock.call_args.kwargs
    )

    assert kwargs["model"] \
        == "gpt-4.1-nano"

    assert kwargs["temperature"] \
        == 0.3

    assert kwargs[
        "max_output_tokens"
    ] == 900

    prompt = kwargs["input"]

    assert "Apple (AAPL)" in prompt
    assert "5.2%" in prompt

    assert (
        "MACD is bullish."
        in prompt
    )

    assert (
        "Do NOT give financial advice."
        in prompt
    )

    assert "Headline 5" in prompt

    assert "Headline 6" \
        not in prompt