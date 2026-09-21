from pathlib import Path

from ingestion.sebi.document_parser import (
    parse_document,
)

from ingestion.sebi.financial_extractor import (
    extract_revenue_metrics_from_block,
    extract_loss_metrics,
    extract_adjusted_ebitda_metrics,
    extract_operating_cash_flow_metrics,
    extract_total_revenue_metrics,
)


class SEBIFinancialSource:
    """
    Extract structured financial metrics from a
    SEBI IPO document.
    """

    def extract_revenue(
        self,
        pdf_path: str | Path,
        *,
        source_document_id: str | None = None,
    ) -> list:
        """
        Parse the PDF and extract revenue metrics.
        """

        pages = parse_document(
            pdf_path
        )

        metrics = []

        for page in pages:

            text = page.get(
                "text",
                "",
            )

            if not text:
                continue

            page_number = (
                page.get("page_number")
                or page.get("page")
            )

            page_metrics = (
                extract_revenue_metrics_from_block(
                    text,
                    source_document_id=(
                        source_document_id
                    ),
                    page_number=page_number,
                )
            )

            metrics.extend(
                page_metrics
            )

        unique_metrics = {}

        for metric in metrics:

            key = (
                metric.metric_name,
                metric.period,
            )

            if key not in unique_metrics:
                unique_metrics[key] = metric

        return list(
            unique_metrics.values()
        )

    def extract_profit_loss(
        self,
        pdf_path: str | Path,
        *,
        source_document_id: str | None = None,
    ) -> list:
        """
        Extract Loss for the Year metrics from a
        SEBI IPO document.
        """

        pages = parse_document(
            pdf_path
        )

        metrics = []

        for page in pages:

            text = page.get(
                "text",
                "",
            )

            if not text:
                continue

            page_number = (
                page.get("page_number")
                or page.get("page")
            )

            page_metrics = (
                extract_loss_metrics(
                    text,
                    source_document_id=(
                        source_document_id
                    ),
                    page_number=page_number,
                )
            )

            metrics.extend(
                page_metrics
            )

        unique_metrics = {}

        for metric in metrics:

            key = (
                metric.metric_name,
                metric.period,
            )

            if key not in unique_metrics:
                unique_metrics[key] = metric

        return list(
            unique_metrics.values()
        )

    def extract_additional_financials(
        self,
        pdf_path: str | Path,
        *,
        source_document_id: str | None = None,
    ) -> list:
        """
        Extract Adjusted EBITDA and operating cash flow.
        """

        pages = parse_document(
            pdf_path
        )

        metrics = []

        for page in pages:

            text = page.get(
                "text",
                "",
            )

            if not text:
                continue

            page_number = (
                page.get("page_number")
                or page.get("page")
            )

            metrics.extend(
                extract_adjusted_ebitda_metrics(
                    text,
                    source_document_id=(
                        source_document_id
                    ),
                    page_number=page_number,
                )
            )

            metrics.extend(
                extract_operating_cash_flow_metrics(
                    text,
                    source_document_id=(
                        source_document_id
                    ),
                    page_number=page_number,
                )
            )

        unique_metrics = {}

        for metric in metrics:

            key = (
                metric.metric_name,
                metric.period,
            )

            if key not in unique_metrics:
                unique_metrics[key] = metric

        return list(
            unique_metrics.values()
        )