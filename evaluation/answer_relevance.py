def keyword_relevance(
    question: str,
    answer: str,
) -> float:
    """
    Simple lexical overlap baseline for answer relevance.

    This is not semantic relevance. It is only a
    deterministic baseline.
    """

    question_words = {
        word.lower()
        for word in question.split()
        if len(word) > 3
    }

    answer_words = {
        word.lower()
        for word in answer.split()
        if len(word) > 3
    }

    if not question_words:
        return 0.0

    overlap = question_words & answer_words

    return len(overlap) / len(question_words)