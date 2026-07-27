import streamlit as st
import plotly.express as px

from technical_indicators import add_all_indicators, technical_summary
from data_pipeline import get_stock_data, get_price_change, get_news
from sentiment import analyze_articles, average_sentiment
from risk import risk_matrix
from llm_summary import generate_market_summary
from db import (
    init_db,
    get_or_create_user,
    save_analysis,
    get_history
)

st.set_page_config(page_title="Market Sentiment Agent", layout="wide")
init_db()

# ---------------------------------------------------------
# AUTHENTICATION GUARD
# ---------------------------------------------------------

if not st.user.is_logged_in:
    st.html("""
    <div style="max-width: 720px; margin: 90px auto 20px auto; background: linear-gradient(135deg, #0f172a, #1e293b); padding: 3.5rem 3rem; border-radius: 24px; color: white; text-align: center; box-shadow: 0 20px 50px rgba(15, 23, 42, 0.15);">
        <div style="font-size: 0.8rem; font-weight: 700; letter-spacing: 0.12em; color: #93c5fd; margin-bottom: 1rem;">
            AI-POWERED MARKET RESEARCH
        </div>

        <h1 style="color: white; font-size: 2.7rem; line-height: 1.15; margin: 0 0 1rem 0;">
            Market Sentiment & News Analyst
        </h1>

        <p style="color: #cbd5e1; font-size: 1.05rem; line-height: 1.7; max-width: 580px; margin: 0 auto;">
            Understand stock movement, news sentiment, and technical indicators through clear, beginner-friendly AI explanations.
        </p>
    </div>
    """)

    left, center, right = st.columns([1.3, 1, 1.3])

    with center:
        st.markdown(
            "<h3 style='text-align: center; margin-bottom: 0.3rem;'>Log In</h3>",
            unsafe_allow_html=True
        )

        st.caption(
            "Sign in with Google to access your dashboard "
            "and personal analysis history."
        )

        st.button(
            "Log In with Google",
            on_click=st.login,
            use_container_width=True,
            type="primary"
        )

    st.stop()

current_user_name = (
    st.user.name
    if hasattr(st.user, "name")
    else "User"
)

current_user_email = (
    st.user.email
    if hasattr(st.user, "email")
    else ""
)

current_user_subject = st.user.sub


user_id = get_or_create_user(
    oidc_subject=current_user_subject,
    name=current_user_name,
    email=current_user_email
)

if (
    "active_user_id"
    not in st.session_state
):
    st.session_state.active_user_id = user_id


if (
    st.session_state.active_user_id
    != user_id
):
    st.session_state.clear()

    st.session_state.active_user_id = user_id

    st.rerun()

st.markdown("""
<style>
.main {
    background-color: #f7f9fc;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

.header-box {
    background: linear-gradient(135deg, #0f172a, #1e293b);
    padding: 2rem;
    border-radius: 18px;
    margin-bottom: 1.5rem;
    color: white;
}

.header-box h1 {
    color: white;
    margin-bottom: 0.4rem;
}

.header-box p {
    color: #cbd5e1;
    font-size: 1rem;
}

.metric-card {
    background-color: white;
    border: 1px solid #e5e7eb;
    padding: 1.3rem;
    border-radius: 16px;
    box-shadow: 0px 4px 12px rgba(15, 23, 42, 0.06);
}

.section-card {
    background-color: white;
    border: 1px solid #e5e7eb;
    padding: 1.5rem;
    border-radius: 16px;
    margin-bottom: 1rem;
    box-shadow: 0px 4px 12px rgba(15, 23, 42, 0.05);
}

.info-box {
    background-color: #eef6ff;
    border-left: 5px solid #2563eb;
    padding: 1rem;
    border-radius: 10px;
    margin-bottom: 1rem;
}

.warning-box {
    background-color: #fff7ed;
    border-left: 5px solid #f97316;
    padding: 1rem;
    border-radius: 10px;
    margin-bottom: 1rem;
}

.news-card {
    background-color: white;
    border: 1px solid #e5e7eb;
    padding: 1.2rem;
    border-radius: 14px;
    margin-bottom: 1rem;
}

.small-label {
    color: #64748b;
    font-size: 0.85rem;
    font-weight: 600;
}

.big-value {
    color: #0f172a;
    font-size: 1.7rem;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header-box">
    <h1>Market Sentiment & News Analyst Agent</h1>
    <p>A beginner-friendly AI dashboard that explains stock price movement, news sentiment, technical indicators, and risk signals in plain English.</p>
</div>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# SIDEBAR USER SECTION
# ---------------------------------------------------------

with st.sidebar:
    user_container = st.container(border=True)

    with user_container:
        st.caption("SIGNED IN AS")
        st.markdown(f"**{current_user_name}**")
        st.caption(current_user_email)

    st.button(
        "Sign Out",
        on_click=st.logout,
        use_container_width=True
    )

    st.divider()


ticker = st.sidebar.text_input(
    "Stock ticker",
    "AAPL"
)

company_name = st.sidebar.text_input(
    "Company name",
    "Apple"
)

st.sidebar.markdown("---")

st.sidebar.write("Example tickers:")

st.sidebar.write(
    "AAPL, TSLA, NVDA, MSFT"
)

if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False

if "ai_summary" not in st.session_state:
    st.session_state.ai_summary = None

if "report_saved" not in st.session_state:
    st.session_state.report_saved = False

if st.sidebar.button("Analyze Stock"):
    with st.spinner("Analyzing stock price, news, and technical indicators..."):
        stock_data = get_stock_data(ticker)

        if stock_data is not None:
            stock_data = add_all_indicators(stock_data)

        price_change = get_price_change(stock_data)
        articles = get_news(ticker, company_name)
        analyzed_articles = analyze_articles(articles)
        avg_sentiment = average_sentiment(analyzed_articles)
        signal = risk_matrix(avg_sentiment, price_change)

        st.session_state.analysis_done = True
        st.session_state.ticker = ticker
        st.session_state.company_name = company_name
        st.session_state.stock_data = stock_data
        st.session_state.price_change = price_change
        st.session_state.analyzed_articles = analyzed_articles
        st.session_state.avg_sentiment = avg_sentiment
        st.session_state.signal = signal
        st.session_state.ai_summary = None
        st.session_state.report_saved = False

if not st.session_state.analysis_done:
    st.markdown("""
    <div class="section-card">
        <h3>How to use this dashboard</h3>
        <p>Enter a stock ticker and company name in the sidebar, then click <b>Analyze Stock</b>.</p>
        <p>The dashboard will collect stock data, read recent news, calculate sentiment, analyze technical indicators, and generate a beginner-friendly market explanation.</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

ticker = st.session_state.ticker
company_name = st.session_state.company_name
stock_data = st.session_state.stock_data
price_change = st.session_state.price_change
analyzed_articles = st.session_state.analyzed_articles
avg_sentiment = st.session_state.avg_sentiment
signal = st.session_state.signal

st.markdown(f"""
<div class="section-card">
    <h2>{company_name} ({ticker.upper()}) Overview</h2>
    <p>This section gives a quick snapshot of the stock's recent movement and news sentiment.</p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="small-label">Price Change</div>
        <div class="big-value">{price_change}%</div>
        <p>How much the stock moved during the selected period.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="small-label">News Sentiment</div>
        <div class="big-value">{avg_sentiment}</div>
        <p>Whether recent news sounds positive, negative, or neutral.</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="small-label">Market Signal</div>
        <div class="big-value" style="font-size:1.1rem;">{signal}</div>
        <p>Compares price movement with news sentiment.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div class="warning-box">
    <b>Beginner note:</b> This app is for research and learning only. It does not tell you what to buy or sell.
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([
    "AI Summary",
    "Technical Charts",
    "News Analysis",
    "History"
])

with tab1:
    st.markdown("""
    <div class="section-card">
        <h2>AI Market Analyst Summary</h2>
        <p>This summary explains the stock in plain English using price movement, news sentiment, and technical indicators.</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Generate Beginner-Friendly AI Summary"):
        with st.spinner("Generating detailed beginner-friendly explanation..."):
            technical_signals = technical_summary(stock_data)

            st.session_state.ai_summary = generate_market_summary(
                ticker=ticker.upper(),
                company_name=company_name,
                price_change=price_change,
                avg_sentiment=avg_sentiment,
                signal=signal,
                technical_signals=technical_signals,
                articles=analyzed_articles
            )

            if not st.session_state.report_saved:
                save_analysis(
                    user_id=user_id,
                    ticker=ticker,
                    company_name=company_name,
                    price_change=price_change,
                    avg_sentiment=avg_sentiment,
                    signal=signal,
                    ai_summary=st.session_state.ai_summary
                )
                st.session_state.report_saved = True

    if st.session_state.ai_summary:
        st.markdown(st.session_state.ai_summary)
    else:
        st.markdown("""
        <div class="info-box">
            Click the button above to generate a detailed explanation written for beginners.
        </div>
        """, unsafe_allow_html=True)

with tab2:
    st.markdown("""
    <div class="section-card">
        <h2>Technical Charts</h2>
        <p>These charts help you understand whether the stock has upward momentum, downward momentum, or mixed signals.</p>
    </div>
    """, unsafe_allow_html=True)

    if stock_data is not None:
        fig = px.line(
            stock_data,
            x="Date",
            y=["Close", "SMA_20", "SMA_50"],
            title=f"{ticker.upper()} Price with Moving Averages"
        )
        st.plotly_chart(fig, width="stretch")

        st.markdown("""
        <div class="info-box">
            <b>Moving averages:</b> These smooth out the stock price so it is easier to see the overall direction. 
            If the price is above the moving averages, that can suggest upward momentum.
        </div>
        """, unsafe_allow_html=True)

        rsi_fig = px.line(
            stock_data,
            x="Date",
            y="RSI",
            title="RSI - Relative Strength Index"
        )
        st.plotly_chart(rsi_fig, width="stretch")

        st.markdown("""
        <div class="info-box">
            <b>RSI:</b> RSI helps show whether a stock may be overheated or undervalued in the short term.
            Above 70 can mean overbought. Below 30 can mean oversold. Between 30 and 70 is usually neutral.
        </div>
        """, unsafe_allow_html=True)

        macd_fig = px.line(
            stock_data,
            x="Date",
            y=["MACD", "Signal_Line"],
            title="MACD vs Signal Line"
        )
        st.plotly_chart(macd_fig, width="stretch")

        st.markdown("""
        <div class="info-box">
            <b>MACD:</b> MACD is a momentum signal. If MACD is above the signal line, it can suggest bullish momentum.
            If it is below the signal line, it can suggest bearish momentum.
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="section-card">
            <h3>Technical Indicator Summary</h3>
        </div>
        """, unsafe_allow_html=True)

        for item in technical_summary(stock_data):
            st.write(f"- {item}")

with tab3:
    st.markdown("""
    <div class="section-card">
        <h2>News Sentiment Breakdown</h2>
        <p>Each article is scored as positive, negative, or neutral based on the headline and description.</p>
    </div>
    """, unsafe_allow_html=True)

    for article in analyzed_articles:
        st.markdown(f"""
        <div class="news-card">
            <h3>{article['title']}</h3>
            <p><b>Source:</b> {article['source']}</p>
            <p><b>Sentiment:</b> {article['sentiment_label']} ({article['sentiment_score']})</p>
            <p>{article['description']}</p>
            <p><a href="{article['url']}" target="_blank">Read full article</a></p>
        </div>
        """, unsafe_allow_html=True)

with tab4:
    st.markdown("""
    <div class="section-card">
        <h2>Historical Sentiment Tracking</h2>
        <p>This section stores completed AI reports so you can track how sentiment changes over time.</p>
    </div>
    """, unsafe_allow_html=True)

    history_df = get_history(
        user_id=user_id,
        ticker=ticker
        )

    if history_df.empty:
        st.info("No saved reports yet. Generate an AI summary first.")
    else:
        st.dataframe(history_df)

        sentiment_fig = px.line(
            history_df,
            x="timestamp",
            y="avg_sentiment",
            title=f"{ticker.upper()} Sentiment Over Time"
        )
        st.plotly_chart(sentiment_fig, width="stretch")

        price_fig = px.line(
            history_df,
            x="timestamp",
            y="price_change",
            title=f"{ticker.upper()} Price Change Over Time"
        )
        st.plotly_chart(price_fig, width="stretch")