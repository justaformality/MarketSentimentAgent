import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_market_summary(
    ticker,
    company_name,
    price_change,
    avg_sentiment,
    signal,
    technical_signals,
    articles
):
    article_summaries = []

    for article in articles[:6]:
        article_summaries.append(
            f"- Title: {article['title']}\n"
            f"  Source: {article['source']}\n"
            f"  Sentiment: {article['sentiment_label']} ({article['sentiment_score']})\n"
            f"  Description: {article['description']}"
        )

    prompt = f"""
You are an AI market analyst assistant for beginner stock market learners.

Your job is to explain this stock in very simple, beginner-friendly language.

Important rules:
- Do NOT give financial advice.
- Do NOT say buy, sell, or hold.
- Explain what the signals mean.
- Use simple words.
- Define any stock market terms briefly.
- Be thorough but easy to understand.
- Mention uncertainty and risk.
- Assume the reader is new to stocks.

Stock:
{company_name} ({ticker})

Price change:
{price_change}%

Average news sentiment:
{avg_sentiment}

Risk matrix signal:
{signal}

Technical indicator signals:
{chr(10).join(technical_signals)}

Recent news articles:
{chr(10).join(article_summaries)}

Write the answer using this exact structure:

## Beginner-Friendly Market Summary

Explain what is happening with the stock in simple terms.

## Price Movement

Explain whether the stock price has been moving up or down and what that may suggest.

## News Sentiment

Explain whether the recent news sounds positive, negative, or mixed.

## Technical Indicators Explained

Explain the moving averages, RSI, and MACD in simple beginner language.

## Risk Level

Classify risk as Low, Medium, or High and explain why.

## What a Beginner Should Watch

List 3 to 5 things a beginner should monitor next.

## Final Takeaway

Give a simple, balanced summary without financial advice.
"""

    response = client.responses.create(
        model="gpt-4.1-nano",
        input=prompt,
        temperature=0.3,
        max_output_tokens=900,
    )

    return response.output_text