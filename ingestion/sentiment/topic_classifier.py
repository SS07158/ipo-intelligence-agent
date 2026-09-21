class TopicClassifier:
    """
    Simple keyword-based classifier for IPO-related news.
    """

    TOPIC_KEYWORDS = {
        "valuation": [
            "valuation",
            "valuations",
            "valued",
            "price band",
            "pricing",
            "premium",
            "gmp",
        ],
        "financials": [
            "revenue",
            "profit",
            "loss",
            "ebitda",
            "earnings",
            "financial",
            "financials",
            "cash flow",
        ],
        "listing": [
            "listing",
            "listed",
            "debut",
            "listing day",
            "listing gain",
            "listing price",
        ],
        "risk": [
            "risk",
            "risks",
            "execution risk",
            "regulatory risk",
            "challenges",
            "concerns",
        ],
        "regulatory": [
            "sebi",
            "regulatory",
            "regulation",
            "approval",
            "compliance",
        ],
        "business": [
            "business",
            "expansion",
            "growth",
            "revenue model",
            "market",
            "customers",
            "stores",
        ],
        "ipo": [
            "ipo",
            "initial public offering",
            "public issue",
            "issue size",
            "price band",
            "offer for sale",
        ],
        "market": [
            "stock market",
            "share market",
            "investors",
            "market sentiment",
            "bullish",
            "bearish",
        ],
    }

    def classify(self, text: str) -> str:
        """
        Return the highest-scoring topic.

        Falls back to 'general' when no topic keywords match.
        """

        if not text or not text.strip():
            return "general"

        text = text.lower()

        scores = {
            topic: 0
            for topic in self.TOPIC_KEYWORDS
        }

        for topic, keywords in self.TOPIC_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    scores[topic] += 1

        best_topic = max(
            scores,
            key=scores.get,
        )

        if scores[best_topic] == 0:
            return "general"

        return best_topic