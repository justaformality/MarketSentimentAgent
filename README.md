# Market Sentiment & News Analyst Agent

[![Tests](https://github.com/justaformality/MarketSentimentAgent/actions/workflows/ci.yml/badge.svg)](https://github.com/justaformality/MarketSentimentAgent/actions/workflows/ci.yml)

A multi-user, beginner-friendly market research dashboard that combines stock price data, financial news sentiment, technical indicators, rule-based signal detection, and AI-generated explanations in one Streamlit application.

The project is designed as an educational and research tool. It does **not** execute trades or provide buy/sell recommendations.

---

## Overview

Stock research can be difficult for beginners because useful information is spread across price charts, financial news, technical indicators, and market commentary.

This application brings those pieces together into a single workflow:

1. A user signs in with Google.
2. The user enters a stock ticker and company name.
3. Historical stock prices are retrieved with `yfinance`.
4. Recent news is retrieved from NewsAPI.
5. VADER scores the sentiment of each article.
6. Technical indicators are calculated from price data.
7. Custom rule-based logic compares sentiment with price movement.
8. An OpenAI model explains the results in beginner-friendly language.
9. Completed analyses are stored in SQLite and tied to the authenticated user.
10. Users can review their saved analysis history.

---

## Features

### Google OIDC Authentication

The application uses Streamlit's built-in OpenID Connect authentication flow.

- Users log in with Google.
- `st.user` provides the authenticated user's identity.
- Each user is mapped to an internal database ID.
- Saved analyses are separated by user.

### Market Data Analysis

The application retrieves approximately six months of historical stock data using `yfinance` and calculates the percentage price change over the retrieved period.

### News Sentiment Analysis

Recent articles are retrieved through NewsAPI.

Each article's title and description are analyzed using VADER Sentiment, producing:

- a compound sentiment score;
- a `Positive`, `Negative`, or `Neutral` label;
- an average sentiment score across the retrieved articles.

### Technical Indicators

The application calculates:

- **20-day Simple Moving Average (SMA 20)**
- **50-day Simple Moving Average (SMA 50)**
- **Relative Strength Index (RSI)**
- **MACD**
- **MACD Signal Line**

It also generates a plain-language technical summary based on the latest values.

### Rule-Based Market Signal

A deterministic risk matrix compares news sentiment with observed price movement.

Possible outputs include:

- `Bullish Confirmation`
- `Bearish Confirmation`
- `Divergence Alert`
- `Neutral / No strong signal`

A divergence is flagged when news sentiment and price movement disagree.

### AI Market Summary

The processed market data is sent to the OpenAI API only after the calculations are complete.

The LLM acts as an **explanation layer**, not as the source of the financial calculations.

The generated report explains:

- recent price movement;
- news sentiment;
- moving averages;
- RSI;
- MACD;
- risk level;
- what a beginner may want to monitor next;
- a balanced final takeaway.

The prompt explicitly instructs the model not to provide buy, sell, or hold recommendations.

### Saved Analysis History

Completed reports are persisted in SQLite.

Each report stores:

- user ID;
- timestamp;
- ticker;
- company name;
- price change;
- average sentiment;
- market signal;
- AI-generated summary.

History queries are filtered by the authenticated user's ID.

### Beginner-Friendly UI

The Streamlit interface includes:

- an authentication page;
- a signed-in user panel;
- overview cards;
- interactive Plotly charts;
- AI summary, technical analysis, news, and history sections;
- plain-language explanations of technical indicators.

---

## Architecture

```text
                         Google OIDC
                              |
                              v
                    Authenticated Streamlit User
                              |
                              v
                       Streamlit Dashboard
                              |
             +----------------+----------------+
             |                                 |
             v                                 v
      Yahoo Finance                         NewsAPI
        via yfinance                          |
             |                                v
             |                         Article Cleaning
             |                                |
             v                                v
      Historical Prices                 VADER Sentiment
             |                                |
             v                                v
   Technical Indicators               Sentiment Scores
   SMA / RSI / MACD                          |
             |                                |
             +---------------+----------------+
                             |
                             v
                    Rule-Based Risk Matrix
                             |
                             v
                   Structured Market Context
                             |
                             v
                       OpenAI API
                             |
                             v
                Beginner-Friendly Explanation
                             |
                             v
                       SQLite Database
                             |
                             v
                  User-Specific Saved History
```

---

## Technology Stack

| Area | Technology |
|---|---|
| Language | Python |
| Frontend | Streamlit |
| Authentication | Streamlit OIDC / Google |
| Stock Data | yfinance |
| News Data | NewsAPI |
| Sentiment Analysis | VADER Sentiment |
| Data Processing | Pandas |
| Technical Analysis | Pandas |
| Visualization | Plotly |
| Generative AI | OpenAI API |
| Database | SQLite |
| Configuration | python-dotenv / Streamlit Secrets |
| Testing | pytest |
| Test Coverage | pytest-cov |

---

## Project Structure

```text
MarketSentimentAgent/
│
├── app.py
├── auth_test.py            # standalone Google sign-in check (see "Testing Google Sign-In")
├── data_pipeline.py
├── db.py
├── llm_summary.py
├── risk.py
├── sentiment.py
├── technical_indicators.py
│
├── tests/
│   ├── test_data_pipeline.py
│   ├── test_llm_summary.py
│   ├── test_risk.py
│   ├── test_sentiment.py
│   └── test_technical_indicators.py
│
├── .streamlit/
│   └── secrets.toml        # you create this; gitignored
│
├── .env                    # you create this; gitignored
├── .github/workflows/ci.yml
├── .gitignore
├── pytest.ini
├── requirements.txt
└── README.md
```

### Main Modules

#### `app.py`

The main Streamlit application and orchestration layer.

It is responsible for:

- authentication;
- user interface;
- session state;
- coordinating the analysis pipeline;
- displaying charts and summaries;
- saving completed reports;
- loading user-specific history.

#### `data_pipeline.py`

Handles external market-data retrieval.

Functions include:

- `get_stock_data()`
- `get_price_change()`
- `get_news()`

#### `sentiment.py`

Contains the NLP sentiment workflow.

Functions include:

- `score_text()`
- `label_sentiment()`
- `analyze_articles()`
- `average_sentiment()`

#### `technical_indicators.py`

Calculates:

- SMA 20;
- SMA 50;
- RSI;
- MACD;
- MACD signal line.

It also creates a beginner-readable technical summary.

#### `risk.py`

Contains deterministic rules that compare average news sentiment with observed price movement.

#### `llm_summary.py`

Builds the structured prompt and calls the OpenAI API to generate the beginner-friendly market explanation.

#### `db.py`

Handles:

- database initialization;
- OIDC user creation and lookup;
- report persistence;
- user-specific report retrieval.

---

# Local Setup

## 1. Clone the repository

```bash
git clone https://github.com/justaformality/MarketSentimentAgent.git
cd MarketSentimentAgent
```

Or open the existing project directory in VS Code.

---

## 2. Create a virtual environment

On macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

On Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

The project currently uses:

```text
streamlit[auth]
plotly
pandas
yfinance
requests
vaderSentiment
python-dotenv
openai
Authlib>=1.3.2
pytest
pytest-cov
```

---

# Environment Configuration

The application requires credentials for NewsAPI, OpenAI, and Google OIDC.

## `.env`

Create a `.env` file in the project root:

```env
NEWS_API_KEY=your_news_api_key
OPENAI_API_KEY=your_openai_api_key
```

Do not commit this file.

---

## Google OIDC Configuration

Create:

```text
.streamlit/secrets.toml
```

Example:

```toml
[auth]
redirect_uri = "http://localhost:8501/oauth2callback"
cookie_secret = "YOUR_RANDOM_COOKIE_SECRET"
client_id = "YOUR_GOOGLE_CLIENT_ID"
client_secret = "YOUR_GOOGLE_CLIENT_SECRET"
server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"
```

For local development, configure the following authorized redirect URI in Google Cloud:

```text
http://localhost:8501/oauth2callback
```

When deploying the application, replace the local redirect URI with the deployed application's callback URL.

Example:

```text
https://your-app.streamlit.app/oauth2callback
```

---

## Generate a Cookie Secret

On macOS/Linux:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(64))"
```

Copy the generated value into `cookie_secret` in `secrets.toml`.

---

# Running the Application

Make sure the virtual environment is active:

```bash
source venv/bin/activate
```

Then run:

```bash
streamlit run app.py
```

Open:

```text
http://localhost:8501
```

The application first displays the Google login page.

After authentication:

1. enter a ticker such as `AAPL`;
2. enter the company name, such as `Apple`;
3. click **Analyze Stock**;
4. review the market overview and technical charts;
5. generate the beginner-friendly AI summary;
6. review news sentiment;
7. view saved analysis history.

---

## Testing Google Sign-In

`auth_test.py` is a minimal Streamlit page for checking your Google OIDC setup on its own, without the API keys or the full dashboard:

```bash
streamlit run auth_test.py
```

If sign-in works, it shows your name, email, and user ID. It is a manual check, not part of the pytest suite.

---

# Testing

The project uses `pytest`.

The tests are designed to run without calling external APIs unnecessarily. GitHub Actions runs the full suite on every push to `main` and on every pull request. No API keys are needed: every external call is mocked, and the OpenAI client is only created on first use.

External services such as Yahoo Finance and OpenAI are mocked where appropriate.

## Run all tests

```bash
python -m pytest
```

For verbose output:

```bash
python -m pytest -v
```

## Run a specific test file

```bash
python -m pytest tests/test_risk.py -v
```

## Run with coverage

```bash
python -m pytest --cov=. --cov-report=term-missing
```

---

## Current Unit-Test Coverage Areas

### `test_risk.py`

Tests:

- bullish confirmation;
- bearish confirmation;
- positive divergence;
- negative divergence;
- neutral conditions;
- rule thresholds.

### `test_sentiment.py`

Tests:

- empty input handling;
- compound-score handling;
- positive/negative/neutral thresholds;
- article enrichment;
- average sentiment calculations.

### `test_technical_indicators.py`

Tests:

- SMA 20;
- SMA 50;
- RSI;
- MACD;
- signal line;
- technical summaries.

### `test_data_pipeline.py`

Tests:

- percentage price change;
- invalid or insufficient price data;
- mocked yfinance responses;
- mocked NewsAPI responses;
- article cleaning.

### `test_llm_summary.py`

Tests:

- OpenAI call configuration;
- prompt construction;
- beginner-focused guardrails;
- article limits;
- structured context passed to the model.

The OpenAI API is mocked during unit testing, so the test suite does not consume API credits.

---

# How the Analysis Pipeline Works

When a user clicks **Analyze Stock**, the application performs the following steps.

### 1. Retrieve Stock Prices

```python
stock_data = get_stock_data(ticker)
```

`yfinance` returns historical stock information as a Pandas DataFrame.

### 2. Calculate Technical Indicators

```python
stock_data = add_all_indicators(stock_data)
```

This enriches the DataFrame with:

```text
SMA_20
SMA_50
RSI
MACD
Signal_Line
```

### 3. Calculate Price Change

```python
price_change = get_price_change(stock_data)
```

The calculation compares the first and latest closing prices in the retrieved dataset.

### 4. Retrieve News

```python
articles = get_news(ticker, company_name)
```

NewsAPI returns recent articles matching the ticker or company name.

### 5. Calculate Sentiment

```python
analyzed_articles = analyze_articles(articles)
avg_sentiment = average_sentiment(analyzed_articles)
```

VADER calculates sentiment for each article using its title and description.

### 6. Generate the Rule-Based Signal

```python
signal = risk_matrix(
    avg_sentiment,
    price_change
)
```

The application checks whether sentiment and price direction confirm or contradict each other.

### 7. Generate the AI Explanation

After the user requests an AI summary:

```python
generate_market_summary(...)
```

The OpenAI model receives the results already calculated by the Python application.

The LLM is used to **explain** the analysis, not to calculate the financial indicators.

### 8. Persist the Report

Completed analyses are stored in SQLite with the current authenticated user's internal ID.

---

# Design Decisions

## Why VADER and an LLM?

The project separates two different NLP tasks.

**VADER** is used for fast, deterministic numerical sentiment scoring.

**OpenAI** is used for natural-language explanation.

This keeps the LLM from being responsible for the core numerical calculations.

## Why Rule-Based Signals?

The market signal is intentionally deterministic.

The same sentiment and price inputs always produce the same result.

This makes the classification transparent and easy to test.

## Why Streamlit?

Streamlit was selected for rapid development of an interactive Python-based MVP while keeping the focus on the market-data and AI pipeline.

## Why SQLite?

SQLite provides lightweight local persistence without requiring separate database infrastructure.

For a larger production deployment, a hosted relational database such as PostgreSQL would be more appropriate.

---

# Known Limitations

This project is an educational MVP and has several important limitations.

### News relevance

The current NewsAPI search uses:

```text
ticker OR company_name
```

Broad company names can sometimes return unrelated articles.

A future version should add stronger relevance filtering or use a finance-specific news provider.

### VADER is not finance-specific

VADER is a general-purpose sentiment model.

A finance-specific model such as FinBERT could improve interpretation of financial language.

### No price prediction

The application does not predict future stock prices.

The rule-based signal only describes the relationship between observed price movement and analyzed news sentiment.

### No automated trading

The application never places trades or connects to a brokerage.

### SQLite is intended for the MVP

For a public multi-user production application, SQLite should be replaced with a hosted database such as PostgreSQL.

### Historical sentiment represents saved analyses

The history section tracks analyses generated by users.

It is not an automatically collected daily historical sentiment dataset.

### External API availability

The application depends on external services including Yahoo Finance, NewsAPI, Google authentication, and OpenAI.

Failures, API limits, or changes to those services can affect application behavior.

---

# Future Improvements

Potential next steps include:

- replace SQLite with PostgreSQL or Supabase;
- automatically resolve the company name from the ticker;
- improve financial-news relevance filtering;
- replace VADER with FinBERT;
- add automated daily sentiment collection;
- add API error handling and retry logic;
- add API usage limits for public users;
- cache repeated market-data requests;
- add database unit tests;
- add Streamlit integration tests;
- add watchlists for multiple stocks;
- deploy through Streamlit Community Cloud;
- add account/history deletion controls;
- add production logging and monitoring.

---

# Author

**Arshia Rajeshnarayanan**

Computer Science graduate and software/AI developer interested in artificial intelligence, interactive applications, data-driven systems, and beginner-friendly technology.


