from dataclasses import dataclass

from transformers import pipeline


@dataclass
class SentimentResult:
    """
    Result produced by the sentiment analyzer.
    """

    label: str
    score: float


class SentimentAnalyzer:
    """
    Financial news sentiment analyzer using FinBERT.
    """

    def __init__(
        self,
        model_name: str = "ProsusAI/finbert",
    ):
        self.classifier = pipeline(
            "sentiment-analysis",
            model=model_name,
            tokenizer=model_name,
        )

    def analyze(
        self,
        text: str,
    ) -> SentimentResult:
        """
        Analyze the sentiment of financial news text.
        """

        if not text or not text.strip():
            return SentimentResult(
                label="neutral",
                score=0.0,
            )

        result = self.classifier(
            text[:2000],
            truncation=True,
        )[0]

        return SentimentResult(
            label=result["label"].lower(),
            score=float(result["score"]),
        )