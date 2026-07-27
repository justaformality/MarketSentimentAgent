from unittest.mock import patch

import pytest

from sentiment import (
    analyze_articles,
    average_sentiment,
    label_sentiment,
    score_text,
)


def test_score_text_empty_returns_zero():
    assert score_text("") == 0
    assert score_text(None) == 0


def test_score_text_uses_vader_compound_score():
    with patch(
        "sentiment.analyzer.polarity_scores",
        return_value={"compound": 0.45678},
    ):
        result = score_text("Example headline")

    assert result == 0.457


@pytest.mark.parametrize(
    ("score", "expected"),
    [
        (0.05, "Positive"),
        (0.80, "Positive"),
        (0.049, "Neutral"),
        (0.0, "Neutral"),
        (-0.049, "Neutral"),
        (-0.05, "Negative"),
        (-0.80, "Negative"),
    ],
)
def test_label_sentiment(score, expected):
    assert label_sentiment(score) == expected


def test_analyze_articles_adds_sentiment_information():
    articles = [
        {
            "title": "Strong earnings",
            "description": "Revenue increased significantly.",
            "url": "https://example.com",
            "source": "Example News",
            "publishedAt": "2026-01-01",
        }
    ]

    with patch(
        "sentiment.score_text",
        return_value=0.7,
    ):
        results = analyze_articles(articles)

    assert len(results) == 1

    result = results[0]

    assert result["title"] == "Strong earnings"
    assert result["sentiment_score"] == 0.7
    assert result["sentiment_label"] == "Positive"


def test_analyze_articles_does_not_modify_original_article():
    articles = [
        {
            "title": "Example",
            "description": "Description",
        }
    ]

    with patch(
        "sentiment.score_text",
        return_value=0.3,
    ):
        analyze_articles(articles)

    assert "sentiment_score" not in articles[0]
    assert "sentiment_label" not in articles[0]


def test_average_sentiment_empty_returns_zero():
    assert average_sentiment([]) == 0


def test_average_sentiment():
    articles = [
        {"sentiment_score": 0.2},
        {"sentiment_score": 0.4},
        {"sentiment_score": -0.1},
    ]

    assert average_sentiment(articles) == 0.167