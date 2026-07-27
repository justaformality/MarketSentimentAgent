import os
import requests
import yfinance as yf
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")


def get_stock_data(ticker: str, period: str = "6mo"):
    stock = yf.Ticker(ticker)
    data = stock.history(period=period)

    if data.empty:
        return None

    data = data.reset_index()
    return data


def get_price_change(stock_data: pd.DataFrame):
    if stock_data is None or len(stock_data) < 2:
        return 0

    first_close = stock_data["Close"].iloc[0]
    last_close = stock_data["Close"].iloc[-1]

    return round(((last_close - first_close) / first_close) * 100, 2)


def get_news(ticker: str, company_name: str):
    url = "https://newsapi.org/v2/everything"

    params = {
        "q": f"{ticker} OR {company_name}",
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 10,
        "apiKey": NEWS_API_KEY,
    }

    response = requests.get(url, params=params)
    response.raise_for_status()

    articles = response.json().get("articles", [])

    cleaned = []
    for article in articles:
        cleaned.append({
            "title": article.get("title", ""),
            "description": article.get("description", ""),
            "url": article.get("url", ""),
            "source": article.get("source", {}).get("name", ""),
            "publishedAt": article.get("publishedAt", "")
        })

    return cleaned