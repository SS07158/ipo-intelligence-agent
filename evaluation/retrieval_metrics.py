def recall_at_k(
    retrieved_sections: list[str],
    expected_sections: list[str],
    k: int,
) -> float:
    """
    Recall@K at the section level.

    Returns 1 if at least one expected section appears
    in the top-k retrieved results, otherwise 0.
    """

    retrieved = retrieved_sections[:k]

    return float(
        any(
            section in expected_sections
            for section in retrieved
        )
    )


def precision_at_k(
    retrieved_sections: list[str],
    expected_sections: list[str],
    k: int,
) -> float:
    """
    Precision@K at the section level.
    """

    retrieved = retrieved_sections[:k]

    if not retrieved:
        return 0.0

    relevant = sum(
        section in expected_sections
        for section in retrieved
    )

    return relevant / len(retrieved)


def reciprocal_rank(
    retrieved_sections: list[str],
    expected_sections: list[str],
) -> float:
    """
    Reciprocal rank of the first relevant result.
    """

    for rank, section in enumerate(
        retrieved_sections,
        start=1,
    ):
        if section in expected_sections:
            return 1.0 / rank

    return 0.0