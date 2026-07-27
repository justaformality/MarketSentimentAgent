from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()


def score_text(text: str):
    if not text:
        return 0

    score = analyzer.polarity_scores(text)
    return round(score["compound"], 3)


def label_sentiment(score: float):
    if score >= 0.05:
        return "Positive"
    elif score <= -0.05:
        return "Negative"
    else:
        return "Neutral"


def analyze_articles(articles):
    results = []

    for article in articles:
        text = f"{article['title']} {article['description']}"
        score = score_text(text)

        results.append({
            **article,
            "sentiment_score": score,
            "sentiment_label": label_sentiment(score)
        })

    return results


def average_sentiment(analyzed_articles):
    if not analyzed_articles:
        return 0

    scores = [article["sentiment_score"] for article in analyzed_articles]
    return round(sum(scores) / len(scores), 3)