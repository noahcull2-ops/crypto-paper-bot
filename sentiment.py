"""
sentiment.py
-----------------
Scores headline sentiment using VADER, a rule-based sentiment
model that runs entirely locally - no API key, no cost, no
external calls. Good enough for headline-level tone (not
deep financial analysis, but useful as one signal among others).

Score ranges from -1.0 (very negative) to +1.0 (very positive).
"""

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

_analyzer = SentimentIntensityAnalyzer()


def score_headlines(headlines: list) -> float:
    """
    Average sentiment across a list of headlines.
    Returns 0.0 (neutral) if the list is empty.
    """
    if not headlines:
        return 0.0

    scores = [_analyzer.polarity_scores(h)["compound"] for h in headlines]
    return sum(scores) / len(scores)
