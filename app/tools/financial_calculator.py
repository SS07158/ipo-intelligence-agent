def percentage_change(
    old_value: float,
    new_value: float,
) -> float:
    """
    Calculate percentage change from old_value to new_value.
    """

    if old_value == 0:
        raise ValueError(
            "old_value cannot be zero."
        )

    return ((new_value - old_value) / old_value) * 100


def cagr(
    start_value: float,
    end_value: float,
    years: int,
) -> float:
    """
    Calculate CAGR as a percentage.
    """

    if start_value <= 0:
        raise ValueError(
            "start_value must be greater than zero."
        )

    if end_value <= 0:
        raise ValueError(
            "end_value must be greater than zero."
        )

    if years <= 0:
        raise ValueError(
            "years must be greater than zero."
        )

    return (
        (end_value / start_value) ** (1 / years) - 1
    ) * 100