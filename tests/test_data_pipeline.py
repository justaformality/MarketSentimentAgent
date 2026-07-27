from unittest.mock import Mock, patch

import pandas as pd

from data_pipeline import (
    get_news,
    get_price_change,
    get_stock_data,
)


def test_get_price_change_none_returns_zero():
    assert get_price_change(None) == 0


def test_get_price_change_single_row_returns_zero():
    data = pd.DataFrame(
        {
            "Close": [100]
        }
    )

    assert get_price_change(data) == 0


def test_get_price_change():
    data = pd.DataFrame(
        {
            "Close": [
                100.0,
                110.0,
                125.0,
            ]
        }
    )

    result = get_price_change(data)

    assert result == 25.0


def test_get_price_change_rounding():
    data = pd.DataFrame(
        {
            "Close": [
                90.0,
                100.0,
            ]
        }
    )

    assert get_price_change(data) == 11.11


def test_get_stock_data():
    history = pd.DataFrame(
        {
            "Close": [
                100.0,
                101.0,
            ]
        },
        index=pd.Index(
            pd.to_datetime(
                [
                    "2026-01-01",
                    "2026-01-02",
                ]
            ),
            name="Date",
        ),
    )

    mocked_ticker = Mock()

    mocked_ticker.history.return_value = (
        history
    )

    with patch(
        "data_pipeline.yf.Ticker",
        return_value=mocked_ticker,
    ) as ticker_class:

        result = get_stock_data(
            "AAPL",
            period="1mo",
        )

    ticker_class.assert_called_once_with(
        "AAPL"
    )

    mocked_ticker.history \
        .assert_called_once_with(
            period="1mo"
        )

    assert result is not None
    assert len(result) == 2

    assert list(result.columns) == [
        "Date",
        "Close",
    ]


def test_get_stock_data_empty_returns_none():
    mocked_ticker = Mock()

    mocked_ticker.history.return_value = (
        pd.DataFrame()
    )

    with patch(
        "data_pipeline.yf.Ticker",
        return_value=mocked_ticker,
    ):
        result = get_stock_data(
            "INVALID"
        )

    assert result is None


def test_get_news():
    mocked_response = Mock()

    mocked_response.json.return_value = {
        "articles": [
            {
                "title": "Apple headline",
                "description":
                    "Apple description",
                "url":
                    "https://example.com",
                "source": {
                    "name":
                        "Example News"
                },
                "publishedAt":
                    "2026-07-01T12:00:00Z",

                # Should be ignored.
                "author":
                    "Example Author",
            }
        ]
    }

    with patch(
        "data_pipeline.requests.get",
        return_value=mocked_response,
    ) as get_mock:

        result = get_news(
            "AAPL",
            "Apple",
        )

    mocked_response.raise_for_status \
        .assert_called_once()

    get_mock.assert_called_once()

    _, kwargs = get_mock.call_args

    params = kwargs["params"]

    assert params["q"] \
        == "AAPL OR Apple"

    assert params["language"] \
        == "en"

    assert params["pageSize"] \
        == 10

    assert result == [
        {
            "title":
                "Apple headline",
            "description":
                "Apple description",
            "url":
                "https://example.com",
            "source":
                "Example News",
            "publishedAt":
                "2026-07-01T12:00:00Z",
        }
    ]


def test_get_news_missing_fields():
    mocked_response = Mock()

    mocked_response.json.return_value = {
        "articles": [{}]
    }

    with patch(
        "data_pipeline.requests.get",
        return_value=mocked_response,
    ):

        result = get_news(
            "AAPL",
            "Apple",
        )

    assert result == [
        {
            "title": "",
            "description": "",
            "url": "",
            "source": "",
            "publishedAt": "",
        }
    ]