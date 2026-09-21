import re

from ingestion.financial_data import (
    StructuredFinancialMetric,
    normalize_metric_name,
)


SIGNED_NUMBER_PATTERN = re.compile(
    r"""
    ^
    (?:
        \(
        \s*
        (?P<negative>
            \d{1,3}
            (?:,\d{3})*
            (?:\.\d+)?
        )
        \s*
        \)
        |
        (?P<positive>
            -?\d{1,3}
            (?:,\d{3})*
            (?:\.\d+)?
        )
    )
    $
    """,
    re.VERBOSE,
)


PERCENTAGE_PATTERN = re.compile(
    r"^-?\d+(?:\.\d+)?%$"
)


def _normalize_lines(
    text: str,
) -> list[str]:
    """
    Normalize PDF-extracted lines while preserving
    their order.
    """

    lines = []

    for line in text.splitlines():

        cleaned = " ".join(
            line.split()
        ).strip()

        if cleaned:
            lines.append(
                cleaned
            )

    return lines


def _parse_number(
    value: str,
) -> float:
    return float(
        value.replace(",", "")
    )

def _parse_signed_number(
    value: str,
) -> float:
    """
    Parse normal and parenthesized financial values.

    Examples:
        1,447.80   -> 1447.80
        -335.32    -> -335.32
        (2,518.58) -> -2518.58
    """

    value = value.strip()

    match = SIGNED_NUMBER_PATTERN.fullmatch(
        value
    )

    if match is None:
        raise ValueError(
            f"Invalid financial number: {value}"
        )

    if match.group("negative") is not None:
        return -float(
            match.group("negative")
            .replace(",", "")
        )

    return float(
        match.group("positive")
        .replace(",", "")
    )


def _is_number_line(
    line: str,
) -> bool:
    """
    Return True when the entire line represents
    a numeric value.
    """

    return (
        SIGNED_NUMBER_PATTERN.fullmatch(
            line
        )
        is not None
    )


def _is_percentage_line(
    line: str,
) -> bool:
    """
    Return True when the line represents a percentage.
    """

    return (
        PERCENTAGE_PATTERN.fullmatch(
            line
        )
        is not None
    )


def _find_total_segment_revenue_values(
    lines: list[str],
) -> tuple[list[float], int] | None:
    """
    Find the flattened 'Total segment revenue' row.

    Supports both representations:

        Total
        segment
        revenue

    and:

        Total segment revenue

    followed by:

        FY2026 value
        FY2026 percentage
        FY2025 value
        FY2025 percentage
        FY2024 value
        FY2024 percentage
    """

    for index, line in enumerate(lines):

        current = (
            line.lower()
            .replace("-", " ")
        )

        # Case 1:
        # "Total segment revenue"
        is_combined = (
            " ".join(
                current.split()
            )
            == "total segment revenue"
        )

        # Case 2:
        # "Total" / "segment" / "revenue"
        is_split = (
            index + 2 < len(lines)
            and lines[index].lower() == "total"
            and lines[index + 1].lower() == "segment"
            and lines[index + 2].lower() == "revenue"
        )

        if is_combined:
            value_start = index + 1

        elif is_split:
            value_start = index + 3

        else:
            continue

        values: list[float] = []

        cursor = value_start

        while (
            cursor < len(lines)
            and len(values) < 3
        ):

            current_line = lines[cursor].strip()

            # Percentage rows are not revenue values.
            if _is_percentage_line(
                current_line
            ):
                cursor += 1
                continue

            if _is_number_line(
                current_line
            ):
                values.append(
                    _parse_number(
                        current_line
                    )
                )

            cursor += 1

        if len(values) == 3:
            return (
                values,
                index,
            )

        return None

    return None


def extract_total_revenue_metrics(
    text: str,
    *,
    source_document_id: str | None = None,
    page_number: int | None = None,
) -> list[StructuredFinancialMetric]:
    """
    Extract total Revenue from Operations from
    the flattened CULT.FIT financial table.
    """

    lines = _normalize_lines(
        text
    )

    result = (
        _find_total_segment_revenue_values(
            lines
        )
    )

    if result is None:
        return []

    values, _ = result

    periods = [
        "FY2026",
        "FY2025",
        "FY2024",
    ]

    metrics = [
        StructuredFinancialMetric(
            metric_name=(
                normalize_metric_name(
                    "Revenue from Operations"
                )
            ),
            period=period,
            value=value,
            unit="INR million",
            source_document_id=(
                source_document_id
            ),
            page_number=page_number,
        )
        for period, value in zip(
            periods,
            values,
        )
    ]

    validate_revenue_metrics(
        metrics
    )

    return metrics

    # return [
    #     StructuredFinancialMetric(
    #         metric_name=(
    #             normalize_metric_name(
    #                 "Revenue from Operations"
    #             )
    #         ),
    #         period=period,
    #         value=value,
    #         unit="INR million",
    #         source_document_id=(
    #             source_document_id
    #         ),
    #         page_number=page_number,
    #     )
    #     for period, value in zip(
    #         periods,
    #         values,
    #     )
    # ]


def extract_revenue_metrics_from_block(
    text: str,
    *,
    source_document_id: str | None = None,
    page_number: int | None = None,
) -> list[StructuredFinancialMetric]:
    """
    Backward-compatible entry point.
    """

    return extract_total_revenue_metrics(
        text,
        source_document_id=source_document_id,
        page_number=page_number,
    )

def validate_revenue_metrics(
    metrics: list[StructuredFinancialMetric],
) -> None:
    """
    Validate extracted revenue metrics before persistence.
    """

    if not metrics:
        raise ValueError(
            "No revenue metrics were extracted."
        )

    expected_periods = {
        "FY2024",
        "FY2025",
        "FY2026",
    }

    actual_periods = {
        metric.period
        for metric in metrics
    }

    if actual_periods != expected_periods:
        raise ValueError(
            "Revenue extraction produced unexpected "
            f"periods: {sorted(actual_periods)}"
        )

    if len(metrics) != 3:
        raise ValueError(
            "Expected exactly three revenue metrics."
        )

    for metric in metrics:

        if metric.metric_name != (
            "revenue_from_operations"
        ):
            raise ValueError(
                "Unexpected revenue metric name: "
                f"{metric.metric_name}"
            )

        if metric.unit != "INR million":
            raise ValueError(
                "Unexpected revenue unit: "
                f"{metric.unit}"
            )

        if metric.value <= 0:
            raise ValueError(
                f"Revenue must be positive: "
                f"{metric.period}={metric.value}"
            )

    periods_in_order = [
        metric.period
        for metric in metrics
    ]

    if periods_in_order != [
        "FY2026",
        "FY2025",
        "FY2024",
    ]:
        raise ValueError(
            "Revenue metrics are not ordered "
            "from FY2026 to FY2024."
        )

def _find_loss_for_year_values(
    lines: list[str],
) -> tuple[list[float], int] | None:
    """
    Find the flattened 'Loss for the year' row.

    Expected structure:

        Loss for the year
        (2,518.58)
        (4,808.26)
        (8,884.91)
    """

    for index, line in enumerate(lines):

        normalized = (
            line.strip()
            .lower()
        )

        if normalized != "loss for the year":
            continue

        values: list[float] = []

        cursor = index + 1

        while (
            cursor < len(lines)
            and len(values) < 3
        ):

            current = (
                lines[cursor]
                .strip()
            )

            # Skip percentages if any appear.
            if "%" in current:
                cursor += 1
                continue

            try:
                value = _parse_signed_number(
                    current
                )

            except ValueError:
                cursor += 1
                continue

            values.append(
                value
            )

            cursor += 1

        if len(values) == 3:
            return (
                values,
                index,
            )

        return None

    return None

def extract_loss_metrics(
    text: str,
    *,
    source_document_id: str | None = None,
    page_number: int | None = None,
) -> list[StructuredFinancialMetric]:
    """
    Extract Loss for the Year from a financial table.
    """

    lines = _normalize_lines(
        text
    )

    result = _find_loss_for_year_values(
        lines
    )

    if result is None:
        return []

    values, _ = result

    periods = [
        "FY2026",
        "FY2025",
        "FY2024",
    ]

    return [
        StructuredFinancialMetric(
            metric_name=(
                normalize_metric_name(
                    "Loss for the year"
                )
            ),
            period=period,
            value=value,
            unit="INR million",
            source_document_id=(
                source_document_id
            ),
            page_number=page_number,
        )
        for period, value in zip(
            periods,
            values,
        )
    ]

def _find_signed_metric_values(
    lines: list[str],
    labels: list[str],
) -> tuple[list[float], int] | None:
    """
    Find a financial metric row and extract its three
    signed values.

    Values may be represented as:

        1,447.80
        (335.32)
        (1,401.90)

    or may be followed by percentage rows.
    """

    normalized_labels = {
        label.lower()
        for label in labels
    }

    for index, line in enumerate(lines):

        normalized = (
            line.strip()
            .lower()
        )

        if normalized not in normalized_labels:
            continue

        values: list[float] = []

        cursor = index + 1

        while (
            cursor < len(lines)
            and len(values) < 3
        ):

            current = (
                lines[cursor]
                .strip()
            )

            if "%" in current:
                cursor += 1
                continue

            try:
                value = _parse_signed_number(
                    current
                )

            except ValueError:
                cursor += 1
                continue

            values.append(
                value
            )

            cursor += 1

        if len(values) == 3:
            return (
                values,
                index,
            )

        return None

    return None

def extract_adjusted_ebitda_metrics(
    text: str,
    *,
    source_document_id: str | None = None,
    page_number: int | None = None,
) -> list[StructuredFinancialMetric]:
    """
    Extract Adjusted EBITDA for FY2026, FY2025 and FY2024.
    """

    lines = _normalize_lines(
        text
    )

    result = _find_signed_metric_values(
        lines,
        [
            "adjusted ebitda",
            "adjusted ebitda(1)",
        ],
    )

    if result is None:
        return []

    values, _ = result

    periods = [
        "FY2026",
        "FY2025",
        "FY2024",
    ]

    return [
        StructuredFinancialMetric(
            metric_name="adjusted_ebitda",
            period=period,
            value=value,
            unit="INR million",
            source_document_id=(
                source_document_id
            ),
            page_number=page_number,
        )
        for period, value in zip(
            periods,
            values,
        )
    ]

def extract_operating_cash_flow_metrics(
    text: str,
    *,
    source_document_id: str | None = None,
    page_number: int | None = None,
) -> list[StructuredFinancialMetric]:
    """
    Extract net cash generated from/(used in)
    operating activities.
    """

    lines = _normalize_lines(
        text
    )

    result = _find_signed_metric_values(
        lines,
        [
            "net cash generated from/ (used in)",
            "net cash generated from/(used in)",
        ],
    )

    if result is None:
        return []

    values, _ = result

    periods = [
        "FY2026",
        "FY2025",
        "FY2024",
    ]

    return [
        StructuredFinancialMetric(
            metric_name="operating_cash_flow",
            period=period,
            value=value,
            unit="INR million",
            source_document_id=(
                source_document_id
            ),
            page_number=page_number,
        )
        for period, value in zip(
            periods,
            values,
        )
    ]