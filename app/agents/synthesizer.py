from app.agents.provenance import (
    FinalAnswer,
    AnswerCitation,
)

from collections import defaultdict


DISPLAY_METRIC_NAMES = {
    "revenue_from_operations": "Revenue from operations",
    "profit_or_loss": "Profit / (loss) for the year",
    "adjusted_ebitda": "Adjusted EBITDA",
    "operating_cash_flow": "Operating cash flow",
}


def format_number(
    value: float,
) -> str:
    """
    Format numeric values consistently.
    """

    return f"{value:,.2f}"


def format_inr_value(
    value: float,
) -> str:
    """
    Format INR values consistently.

    Example:
        9266.62  -> ₹9,266.62
        -8884.91 -> -₹8,884.91
    """

    if value < 0:
        return f"-₹{abs(value):,.2f}"

    return f"₹{value:,.2f}"


def format_citation(
    citation_data: dict | None,
) -> str:
    """
    Convert citation metadata into a human-readable
    citation string.

    Example:
        [DRHP, SEBI, p. 52]
    """

    if not citation_data:
        return ""

    document_type = citation_data.get(
        "document_type"
    )

    source = citation_data.get(
        "source"
    )

    page_number = citation_data.get(
        "page_number"
    )

    section = citation_data.get(
        "section"
    )

    parts = []

    if document_type:
        parts.append(
            str(document_type)
        )

    if source:
        parts.append(
            str(source)
        )

    if page_number is not None:
        parts.append(
            f"p. {page_number}"
        )

    if section:
        parts.append(
            str(section)
        )

    if not parts:
        return ""

    return (
        " ["
        + ", ".join(parts)
        + "]"
    )


def build_metric_citation(
    company_name: str,
    detail: dict | None,
) -> dict | None:
    """
    Convert metric provenance into the citation
    structure expected by AnswerCitation.
    """

    if not detail:
        return None

    return {
        "company": company_name,
        "document_id": str(
            detail.get(
                "source_document_id"
            )
        )
        if detail.get(
            "source_document_id"
        ) is not None
        else None,
        "document_type": "DRHP",
        "source": "SEBI",
        "page_number": detail.get(
            "page_number"
        ),
    }


def synthesize_tool_results(
    question: str,
    tool_results: list[dict],
) -> FinalAnswer:
    """
    Deterministically synthesize the final answer
    from tool outputs.

    The LLM is not used for final factual assembly.
    """

    question_normalized = question.lower()

    is_risk_question = any(
        phrase in question_normalized
        for phrase in [
            "risk",
            "risks",
            "risk factors",
            "internal risk",
            "internal risks",
            "external risk",
            "external risks",
        ]
    )

    
    financial_results = []
    risk_results = []
    news_results = []
    ipo_results = []
    document_results = []
    citations: list[AnswerCitation] = []

    for item in tool_results:

        tool_name = item["tool"]
        result = item["result"]

        if tool_name in {
            "lookup_financials_tool",
            "analyze_revenue_growth_tool",
            "analyze_financial_performance_tool",
        }:
            financial_results.append(result)

        elif tool_name == "search_ipo_documents_tool":
            document_results.append(result)

        elif tool_name == "lookup_news_tool":
            news_results.append(result)

        elif tool_name == "lookup_ipo_tool":
            ipo_results.append(result)

    parts = []

    normalized_question = question.lower()

    # -------------------------------------------------
    # DOCUMENT HEADING
    # -------------------------------------------------

    market_share_terms = [
        "market share",
        "share of the market",
        "market position",
        "industry share",
    ]

    post_listing_terms = [
        "after ipo listing",
        "after listing",
        "post ipo listing",
        "post-listing",
        "post listing",
        "listing outcome",
        "expected outcome after ipo",
    ]

    risk_terms = [
        "risk",
        "risks",
        "risk factors",
        "threat",
    ]

    if any(
        term in normalized_question
        for term in market_share_terms
    ):
        document_heading = "Market / industry findings"

    elif any(
        term in normalized_question
        for term in post_listing_terms
    ):
        document_heading = "Post-listing considerations"

    elif any(
        term in normalized_question
        for term in risk_terms
    ):
        document_heading = "Risks"

    else:
        document_heading = "Document findings"

    # -------------------------------------------------
    # NEWS
    # -------------------------------------------------

    if news_results:

        news_lines = []

        for result in news_results:

            if not isinstance(
                result,
                dict,
            ):
                continue

            company_name = result.get(
                "company_name",
                "The company",
            )

            articles = result.get(
                "articles",
                [],
            )

            if not articles:
                news_lines.append(
                    f"No recent news articles are "
                    f"currently available for "
                    f"{company_name}."
                )
                continue

            for article in articles:

                if not isinstance(
                    article,
                    dict,
                ):
                    continue

                title = article.get(
                    "title",
                    "Untitled article",
                )

                source = article.get(
                    "source",
                    "Unknown source",
                )

                published_at = article.get(
                    "published_at",
                )

                sentiment = article.get(
                    "sentiment",
                    {},
                )

                topic = article.get(
                    "topic",
                )

                url = article.get(
                    "url"
                )

                line = (
                    f"- {title} "
                    f"({source})"
                )

                if published_at:
                    line += (
                        f" — {published_at}"
                    )

                if (
                    isinstance(sentiment, dict)
                    and sentiment.get("label")
                ):
                    line += (
                        f" | Sentiment: "
                        f"{sentiment['label']}"
                    )

                if topic:
                    line += (
                        f" | Topic: {topic}"
                    )

                if url:
                    line += (
                        f" — [Open article]({url})"
                    )

                news_lines.append(line)

                

        if news_lines:
            parts.append(
                "News:\n"
                + "\n".join(news_lines)
            )

    # -------------------------------------------------
    # REVENUE ANALYSIS
    # -------------------------------------------------

    growth_result = next(
        (
            result
            for result in financial_results
            if (
                isinstance(result, dict)
                and result.get(
                    "start_value"
                ) is not None
                and result.get(
                    "end_value"
                ) is not None
            )
        ),
        None,
    )

    if growth_result is not None:

        start_period = growth_result.get(
            "start_period",
            "start period",
        )

        end_period = growth_result.get(
            "end_period",
            "end period",
        )

        start_value = growth_result[
            "start_value"
        ]

        end_value = growth_result[
            "end_value"
        ]

        unit = growth_result.get(
            "unit",
            "INR million",
        )

        unit_display = unit.replace(
            "INR ",
            "",
        )

        total_growth = growth_result.get(
            "total_growth_percent"
        )

        cagr = growth_result.get(
            "cagr_percent"
        )

        revenue_text = (
            "Revenue from operations increased "
            f"from {format_inr_value(start_value)} "
            f"{unit_display} "
            f"in {start_period} to "
            f"{format_inr_value(end_value)} "
            f"{unit_display} "
            f"in {end_period}."
        )

        if total_growth is not None:
            revenue_text += (
                f" Total growth was "
                f"{total_growth:.2f}%."
            )

        if cagr is not None:
            revenue_text += (
                f" CAGR was "
                f"{cagr:.2f}%."
            )

        parts.append(
            "Revenue:\n"
            + revenue_text
        )

        # Add citations returned directly
        # by the revenue analysis tool.
        for citation_data in growth_result.get(
            "citations",
            [],
        ):
            if citation_data:

                citations.append(
                    AnswerCitation(
                        claim=revenue_text,
                        citation=citation_data,
                    )
                )

    # -------------------------------------------------
    # DIRECT FINANCIAL LOOKUP
    # -------------------------------------------------

    else:

        metrics = []

        for result in financial_results:

            if not isinstance(
                result,
                dict,
            ):
                continue

            # The financial-performance result
            # is handled in its own section below.
            if (
                "metric_details" in result
                and "analysis" in result
            ):
                continue

            result_metrics = result.get(
                "metrics",
                [],
            )

            if isinstance(
                result_metrics,
                list,
            ):
                metrics.extend(
                    result_metrics
                )

            elif isinstance(
                result_metrics,
                dict,
            ):
                for metric_name, period_values in result_metrics.items():

                    if not isinstance(
                        period_values,
                        dict,
                    ):
                        continue

                    for period, value in period_values.items():

                        metrics.append(
                            {
                                "metric_name": metric_name,
                                "period": period,
                                "value": value,
                            }
                        )

        if metrics:

            metric_lines = []

            grouped_metrics = defaultdict(list)

            for metric in metrics:

                raw_metric_name = metric.get(
                    "metric_name",
                    "Unknown metric",
                )

                period = metric.get(
                    "period",
                    "Unknown period",
                )

                value = metric.get(
                    "value"
                )

                if value is None:
                    continue

                grouped_metrics[
                    raw_metric_name
                ].append(
                    {
                        "period": period,
                        "value": value,
                        "citation": metric.get(
                            "citation"
                        ),
                    }
                )

            for raw_metric_name, values in grouped_metrics.items():

                metric_name = DISPLAY_METRIC_NAMES.get(
                    raw_metric_name,
                    raw_metric_name,
                )

                metric_lines.append(
                    f"{metric_name}:"
                )

                for item in values:

                    period = item[
                        "period"
                    ]

                    value = item[
                        "value"
                    ]

                    citation_data = item.get(
                        "citation"
                    )

                    citation_text = format_citation(
                        citation_data
                    )

                    metric_lines.append(
                        f"- {period}: "
                        f"{format_inr_value(value)} "
                        f"million"
                        f"{citation_text}"
                    )

                    if citation_data:

                        claim = (
                            f"{metric_name} for "
                            f"{period} was "
                            f"{format_inr_value(value)} "
                            f"million."
                        )

                        citations.append(
                            AnswerCitation(
                                claim=claim,
                                citation=citation_data,
                            )
                        )

                metric_lines.append("")

            parts.append(
                document_heading + ":\n"
                + "\n\n".join(
                    metric_lines
                )
            )

        source_lines = []

        seen_sources = set()

        for result in risk_results:

            if not isinstance(
                result,
                dict,
            ):
                continue

            evidence = result.get(
                "evidence",
                [],
            )

            for evidence_item in evidence:

                if not isinstance(
                    evidence_item,
                    dict,
                ):
                    continue

                citation_data = evidence_item.get(
                    "citation"
                )

                if not citation_data:
                    continue

                document_type = citation_data.get(
                    "document_type"
                )

                source = citation_data.get(
                    "source"
                )

                page_number = citation_data.get(
                    "page_number"
                )

                section = citation_data.get(
                    "section"
                )

                source_key = (
                    document_type,
                    source,
                    page_number,
                    section,
                )

                if source_key in seen_sources:
                    continue

                seen_sources.add(
                    source_key
                )

                citation_text = format_citation(
                    citation_data
                )

                source_lines.append(
                    f"- {citation_text.strip()}"
                )

        if source_lines:

            parts.append(
                "Sources:\n"
                + "\n".join(
                    source_lines
                )
            )



    # -------------------------------------------------
    # FINANCIAL PERFORMANCE
    # -------------------------------------------------

    performance_result = next(
        (
            item["result"]
            for item in tool_results
            if (
                item["tool"]
                == "analyze_financial_performance_tool"
            )
            and isinstance(
                item["result"],
                dict,
            )
            and item["result"].get(
                "found"
            )
            is True
        ),
        None,
    )

    if performance_result is not None:

        company_name = performance_result[
            "company_name"
        ]

        performance_metrics = performance_result.get(
            "metrics",
            {},
        )

        metric_details = performance_result.get(
            "metric_details",
            {},
        )

        analysis = performance_result.get(
            "analysis",
            {},
        )

        parts.append(
            f"{company_name}'s financial performance "
            f"changed as follows:"
        )

    

        # -------------------------------------------------
        # Revenue
        # -------------------------------------------------

        revenue = performance_metrics.get(
            "revenue_from_operations",
            {},
        )

        revenue_details = metric_details.get(
            "revenue_from_operations",
            {},
        )

        if revenue:

            periods = sorted(
                revenue.keys()
            )

            if periods:

                first_period = periods[0]
                last_period = periods[-1]

                first_value = revenue[
                    first_period
                ]

                last_value = revenue[
                    last_period
                ]

                first_detail = revenue_details.get(
                    first_period
                )

                last_detail = revenue_details.get(
                    last_period
                )

                first_citation_data = (
                    build_metric_citation(
                        company_name,
                        first_detail,
                    )
                )

                last_citation_data = (
                    build_metric_citation(
                        company_name,
                        last_detail,
                    )
                )

                first_citation = format_citation(
                    first_citation_data
                )

                last_citation = format_citation(
                    last_citation_data
                )

                revenue_claim = (
                    f"Revenue from operations "
                    f"increased from "
                    f"{format_inr_value(first_value)} "
                    f"million "
                    f"({first_period})"
                    f"{first_citation} "
                    f"to "
                    f"{format_inr_value(last_value)} "
                    f"million "
                    f"({last_period})"
                    f"{last_citation}, "
                    f"representing "
                    f"{analysis.get('revenue_growth_percent', 0):.2f}% "
                    f"growth."
                )

                parts.append(
                    revenue_claim
                )

                if first_citation_data:

                    citations.append(
                        AnswerCitation(
                            claim=revenue_claim,
                            citation=first_citation_data,
                        )
                    )

                if last_citation_data:

                    citations.append(
                        AnswerCitation(
                            claim=revenue_claim,
                            citation=last_citation_data,
                        )
                    )

        # -------------------------------------------------
        # Profit / Loss
        # -------------------------------------------------

        profit_loss = performance_metrics.get(
            "profit_or_loss",
            {},
        )

        profit_loss_details = metric_details.get(
            "profit_or_loss",
            {},
        )

        if profit_loss:

            periods = sorted(
                profit_loss.keys()
            )

            if periods:

                first_period = periods[0]
                last_period = periods[-1]

                first_value = profit_loss[
                    first_period
                ]

                last_value = profit_loss[
                    last_period
                ]

                first_detail = profit_loss_details.get(
                    first_period
                )

                last_detail = profit_loss_details.get(
                    last_period
                )

                first_citation_data = (
                    build_metric_citation(
                        company_name,
                        first_detail,
                    )
                )

                last_citation_data = (
                    build_metric_citation(
                        company_name,
                        last_detail,
                    )
                )

                first_citation = format_citation(
                    first_citation_data
                )

                last_citation = format_citation(
                    last_citation_data
                )

                if (
                    first_value < 0
                    and last_value < 0
                ):

                    profit_loss_claim = (
                        f"The loss narrowed from "
                        f"{format_inr_value(first_value)} "
                        f"million "
                        f"({first_period})"
                        f"{first_citation} "
                        f"to "
                        f"{format_inr_value(last_value)} "
                        f"million "
                        f"({last_period})"
                        f"{last_citation}."
                    )

                elif (
                    first_value < 0
                    and last_value >= 0
                ):

                    profit_loss_claim = (
                        f"Profit/loss improved from "
                        f"a loss of "
                        f"{format_inr_value(first_value)} "
                        f"million "
                        f"({first_period})"
                        f"{first_citation} "
                        f"to a profit of "
                        f"{format_inr_value(last_value)} "
                        f"million "
                        f"({last_period})"
                        f"{last_citation}."
                    )

                else:

                    profit_loss_claim = (
                    f"The loss narrowed from "
                    f"₹{abs(first_value):,.2f} "
                    f"million "
                    f"({first_period})"
                    f"{first_citation} "
                    f"to "
                    f"₹{abs(last_value):,.2f} "
                    f"million "
                    f"({last_period})"
                    f"{last_citation}."
                )

                parts.append(
                    profit_loss_claim
                )

                if first_citation_data:

                    citations.append(
                        AnswerCitation(
                            claim=profit_loss_claim,
                            citation=first_citation_data,
                        )
                    )

                if last_citation_data:

                    citations.append(
                        AnswerCitation(
                            claim=profit_loss_claim,
                            citation=last_citation_data,
                        )
                    )

        # -------------------------------------------------
        # Adjusted EBITDA
        # -------------------------------------------------

        ebitda = performance_metrics.get(
            "adjusted_ebitda",
            {},
        )

        ebitda_details = metric_details.get(
            "adjusted_ebitda",
            {},
        )

        if ebitda:

            periods = sorted(
                ebitda.keys()
            )

            if periods:

                first_period = periods[0]
                last_period = periods[-1]

                first_value = ebitda[
                    first_period
                ]

                last_value = ebitda[
                    last_period
                ]

                first_detail = ebitda_details.get(
                    first_period
                )

                last_detail = ebitda_details.get(
                    last_period
                )

                first_citation_data = (
                    build_metric_citation(
                        company_name,
                        first_detail,
                    )
                )

                last_citation_data = (
                    build_metric_citation(
                        company_name,
                        last_detail,
                    )
                )

                first_citation = format_citation(
                    first_citation_data
                )

                last_citation = format_citation(
                    last_citation_data
                )

                if (
                    first_value < 0
                    and last_value >= 0
                ):

                    ebitda_claim = (
                        f"Adjusted EBITDA improved "
                        f"from "
                        f"{format_inr_value(first_value)} "
                        f"million "
                        f"({first_period})"
                        f"{first_citation} "
                        f"to "
                        f"{format_inr_value(last_value)} "
                        f"million "
                        f"({last_period})"
                        f"{last_citation}, "
                        f"moving from negative "
                        f"to positive."
                    )

                else:

                    ebitda_claim = (
                        f"Adjusted EBITDA changed "
                        f"from "
                        f"{format_inr_value(first_value)} "
                        f"million "
                        f"({first_period})"
                        f"{first_citation} "
                        f"to "
                        f"{format_inr_value(last_value)} "
                        f"million "
                        f"({last_period})"
                        f"{last_citation}."
                    )

                parts.append(
                    ebitda_claim
                )

                if first_citation_data:

                    citations.append(
                        AnswerCitation(
                            claim=ebitda_claim,
                            citation=first_citation_data,
                        )
                    )

                if last_citation_data:

                    citations.append(
                        AnswerCitation(
                            claim=ebitda_claim,
                            citation=last_citation_data,
                        )
                    )

        # -------------------------------------------------
        # Operating Cash Flow
        # -------------------------------------------------

        operating_cash_flow = performance_metrics.get(
            "operating_cash_flow",
            {},
        )

        operating_cash_flow_details = metric_details.get(
            "operating_cash_flow",
            {},
        )

        if operating_cash_flow:

            periods = sorted(
                operating_cash_flow.keys()
            )

            if periods:

                first_period = periods[0]
                last_period = periods[-1]

                first_value = operating_cash_flow[
                    first_period
                ]

                last_value = operating_cash_flow[
                    last_period
                ]

                first_detail = operating_cash_flow_details.get(
                    first_period
                )

                last_detail = operating_cash_flow_details.get(
                    last_period
                )

                first_citation_data = (
                    build_metric_citation(
                        company_name,
                        first_detail,
                    )
                )

                last_citation_data = (
                    build_metric_citation(
                        company_name,
                        last_detail,
                    )
                )

                first_citation = format_citation(
                    first_citation_data
                )

                last_citation = format_citation(
                    last_citation_data
                )

                if (
                    first_value < 0
                    and last_value >= 0
                ):

                    cash_flow_claim = (
                        f"Operating cash flow improved "
                        f"from "
                        f"{format_inr_value(first_value)} "
                        f"million "
                        f"({first_period})"
                        f"{first_citation} "
                        f"to "
                        f"{format_inr_value(last_value)} "
                        f"million "
                        f"({last_period})"
                        f"{last_citation}, "
                        f"moving from negative "
                        f"to positive."
                    )

                else:

                    cash_flow_claim = (
                        f"Operating cash flow changed "
                        f"from "
                        f"{format_inr_value(first_value)} "
                        f"million "
                        f"({first_period})"
                        f"{first_citation} "
                        f"to "
                        f"{format_inr_value(last_value)} "
                        f"million "
                        f"({last_period})"
                        f"{last_citation}."
                    )

                parts.append(
                    cash_flow_claim
                )

                if first_citation_data:

                    citations.append(
                        AnswerCitation(
                            claim=cash_flow_claim,
                            citation=first_citation_data,
                        )
                    )

                if last_citation_data:

                    citations.append(
                        AnswerCitation(
                            claim=cash_flow_claim,
                            citation=last_citation_data,
                        )
                    )
   
    # -------------------------------------------------
    # DOCUMENT FINDINGS
    # -------------------------------------------------

    document_lines = []

    for result in document_results:

        if not isinstance(
            result,
            dict,
        ):
            continue

        evidence = result.get(
            "evidence",
            [],
        )

        answer = result.get(
            "answer",
            "",
        ).strip()

        if evidence and answer:

            document_lines.append(
                answer
            )

            for evidence_item in evidence:

                citation_data = (
                    evidence_item.get(
                        "citation"
                    )
                )

                if citation_data:

                    citation_data = dict(
                        citation_data
                    )

                    metadata = evidence_item.get(
                        "metadata",
                        {}
                    )

                    if (
                        "source_url" not in citation_data
                        and isinstance(metadata, dict)
                    ):
                        citation_data["source_url"] = (
                            metadata.get("source_url")
                        )

                    citations.append(
                        AnswerCitation(
                            claim=answer,
                            citation=citation_data,
                        )
                    )

    if document_lines:

        normalized_question = (
            question.lower()
        )

        risk_question = any(
            term in normalized_question
            for term in [
                "risk",
                "risks",
            ]
        )

        market_share_question = any(
            term in normalized_question
            for term in [
                "market share",
                "market position",
                "share of the market",
            ]
        )

        listing_question = any(
            term in normalized_question
            for term in [
                "after ipo listing",
                "after the ipo listing",
                "post listing",
                "post-listing",
                "listing outcome",
                "after listing",
            ]
        )

        if risk_question:
            heading = "Risks:"

        elif market_share_question:
            heading = "Market / industry findings:"

        elif listing_question:
            heading = (
                "Post-listing considerations:"
            )

        else:
            heading = "Document findings:"

        parts.append(
            heading
            + "\n"
            + "\n\n".join(
                document_lines
            )
        )

    elif document_results:

        normalized_question = (
            question.lower()
        )

        if "risk" in normalized_question:
            heading = "Risks:"
        else:
            heading = "Document findings:"

        parts.append(
            document_heading + ":\n"
            + "The available document "
               "evidence was insufficient "
               "to answer this part of "
               "the question."
            )

    # -------------------------------------------------
    # IPO INFORMATION
    # -------------------------------------------------

    if ipo_results:

        ipo_lines = []

        for result in ipo_results:

            if not isinstance(
                result,
                dict,
            ):
                continue

            if result.get("found") is not True:
                message = result.get(
                    "message",
                    "IPO information was not found.",
                )

                ipo_lines.append(
                    message
                )

                continue

            ipo = result.get(
                "ipo",
                {},
            )

            if not isinstance(
                ipo,
                dict,
            ):
                continue

            company_name = ipo.get(
                "company_name",
                "The company",
            )

            question_normalized = question.lower()

            # Fresh issue
            if (
                "fresh issue" in question_normalized
                and ipo.get("fresh_issue") is not None
            ):
                ipo_lines.append(
                    f"{company_name}'s proposed fresh issue "
                    f"size is ₹{ipo['fresh_issue']} crore."
                )

            # Lot size
            elif (
                "lot size" in question_normalized
                and ipo.get("lot_size") is not None
            ):
                ipo_lines.append(
                    f"The IPO lot size is "
                    f"{ipo['lot_size']} shares."
                )

            # Issue size
            elif (
                "issue size" in question_normalized
                and ipo.get("issue_size") is not None
            ):
                ipo_lines.append(
                    f"The IPO issue size is "
                    f"{ipo['issue_size']}."
                )

            # Price band
            elif (
                "price band" in question_normalized
                and (
                    ipo.get("price_band_low") is not None
                    or ipo.get("price_band_high") is not None
                )
            ):
                low = ipo.get(
                    "price_band_low"
                )
                high = ipo.get(
                    "price_band_high"
                )

                ipo_lines.append(
                    f"The IPO price band is "
                    f"₹{low} to ₹{high}."
                )

            # Listing date
            elif (
                "listing date" in question_normalized
                and ipo.get("listing_date") is not None
            ):
                ipo_lines.append(
                    f"The expected listing date is "
                    f"{ipo['listing_date']}."
                )

            # Issue dates
            elif (
                "issue date" in question_normalized
                or "open date" in question_normalized
                or "close date" in question_normalized
            ):
                open_date = ipo.get(
                    "issue_open_date"
                )
                close_date = ipo.get(
                    "issue_close_date"
                )

                ipo_lines.append(
                    f"The IPO is scheduled to open on "
                    f"{open_date} and close on "
                    f"{close_date}."
                )

            # Generic fallback for IPO lookup
            else:
                available = []

                if ipo.get("issue_size") is not None:
                    available.append(
                        f"Issue size: {ipo['issue_size']}"
                    )

                if ipo.get("fresh_issue") is not None:
                    available.append(
                        f"Fresh issue: ₹{ipo['fresh_issue']} crore"
                    )

                if ipo.get("offer_for_sale") is not None:
                    available.append(
                        f"Offer for sale: {ipo['offer_for_sale']}"
                    )

                if ipo.get("lot_size") is not None:
                    available.append(
                        f"Lot size: {ipo['lot_size']} shares"
                    )

                if available:
                    ipo_lines.append(
                        "\n".join(available)
                    )

        if ipo_lines:
            parts.append(
                "IPO:\n"
                + "\n".join(ipo_lines)
            )

    # -------------------------------------------------
    # DOCUMENT ANSWER
    # -------------------------------------------------

    if document_results and not is_risk_question:

        document_lines = []

        for result in document_results:

            if not isinstance(result, dict):
                continue

            answer = result.get(
                "answer",
                "",
            ).strip()

            evidence = result.get(
                "evidence",
                [],
            )

            if answer:
                document_lines.append(
                    answer
                )

                

        
    # -------------------------------------------------
    # FALLBACK
    # -------------------------------------------------

    if not parts:

        return FinalAnswer(
            answer=(
                "The available tool results were "
                "insufficient to answer the question."
            ),
            citations=[],
        )

    return FinalAnswer(
        answer="\n\n".join(parts),
        citations=citations,
    )