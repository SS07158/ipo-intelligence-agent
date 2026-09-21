from pathlib import Path

from ingestion.financial_persistence import (
    persist_financial_metrics,
)

from ingestion.sebi.financial_source import (
    SEBIFinancialSource,
)


class SEBIFinancialIngestion:
    """
    Extract financial metrics from a SEBI document
    and persist them into SQL.
    """

    def __init__(
        self,
        source: SEBIFinancialSource | None = None,
    ):
        self.source = (
            source
            or SEBIFinancialSource()
        )

    def ingest_financials(
        self,
        *,
        ipo_id: str,
        pdf_path: str | Path,
        document_id: str,
    ) -> dict:
        """
        Extract financial metrics from a SEBI document
        and persist them.
        """

        revenue_metrics = (
            self.source.extract_revenue(
                pdf_path,
                source_document_id=document_id,
            )
        )

        profit_loss_metrics = (
            self.source.extract_profit_loss(
                pdf_path,
                source_document_id=document_id,
            )
        )

        additonal_metrics = (
            self.source.extract_additional_financials(
                pdf_path,
                source_document_id=document_id,
            )
        )

        metrics = (
            revenue_metrics
            + profit_loss_metrics
            + additonal_metrics
        )

        if not metrics:
            return {
                "success": False,
                "ipo_id": ipo_id,
                "message": (
                    "No financial metrics were "
                    "extracted from the document."
                ),
                "inserted": 0,
            }

        result = persist_financial_metrics(
            ipo_id=ipo_id,
            metrics=metrics,
        )

        result["metric_count"] = len(
            metrics
        )

        return result

    def ingest_revenue(
        self,
        *,
        ipo_id: str,
        pdf_path: str | Path,
        document_id: str,
    ) -> dict:
        """
        Backward-compatible revenue-only ingestion.
        """

        return self.ingest_financials(
            ipo_id=ipo_id,
            pdf_path=pdf_path,
            document_id=document_id,
        )