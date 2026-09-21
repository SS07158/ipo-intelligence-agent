from database.database import SessionLocal
from database.ipo_repository import (
    get_ipo_by_id,
    get_financial_document_id,
    get_or_create_financial_metric,
)

from ingestion.financial_data import (
    StructuredFinancialMetric,
)


from database.database import SessionLocal
from database.ipo_repository import (
    get_financial_document_id,
    get_financial_metrics,
    get_ipo_by_id,
    create_financial_metric,
)

from ingestion.financial_data import (
    StructuredFinancialMetric,
)


def persist_financial_metrics(
    *,
    ipo_id: str,
    metrics: list[StructuredFinancialMetric],
) -> dict:
    """
    Persist financial metrics while tracking whether
    each metric was created or updated.
    """

    session = SessionLocal()

    try:

        ipo = get_ipo_by_id(
            session,
            ipo_id,
        )

        if ipo is None:
            return {
                "success": False,
                "message": (
                    f"IPO not found: {ipo_id}"
                ),
                "created": 0,
                "updated": 0,
                "total": 0,
            }

        created = 0
        updated = 0
        persisted = []

        for metric in metrics:

            source_document_id = None

            if (
                metric.source_document_id
                is not None
            ):
                source_document_id = (
                    get_financial_document_id(
                        session,
                        metric.source_document_id,
                    )
                )

                if source_document_id is None:
                    raise ValueError(
                        "Source document not found: "
                        f"{metric.source_document_id}"
                    )

            existing_metrics = (
                get_financial_metrics(
                    session,
                    ipo_id=ipo.id,
                    metric_name=(
                        metric.metric_name
                    ),
                    period=metric.period,
                )
            )

            if existing_metrics:

                existing = (
                    existing_metrics[0]
                )

                existing.value = (
                    metric.value
                )

                existing.unit = (
                    metric.unit
                )

                existing.source_document_id = (
                    source_document_id
                )

                existing.page_number = (
                    metric.page_number
                )

                updated += 1

                saved = existing

            else:

                saved = (
                    create_financial_metric(
                        session,
                        ipo_id=ipo.id,
                        metric_name=(
                            metric.metric_name
                        ),
                        period=metric.period,
                        value=metric.value,
                        unit=metric.unit,
                        source_document_id=(
                            source_document_id
                        ),
                        page_number=(
                            metric.page_number
                        ),
                    )
                )

                created += 1

            persisted.append(
                {
                    "id": saved.id,
                    "metric_name": (
                        saved.metric_name
                    ),
                    "period": saved.period,
                    "value": saved.value,
                    "unit": saved.unit,
                    "source_document_id": (
                        saved.source_document_id
                    ),
                    "page_number": (
                        saved.page_number
                    ),
                }
            )

        return {
            "success": True,
            "ipo_id": ipo_id,
            "company_name": (
                ipo.company_name
            ),
            "created": created,
            "updated": updated,
            "total": len(persisted),
            "metrics": persisted,
        }

    finally:
        session.close()