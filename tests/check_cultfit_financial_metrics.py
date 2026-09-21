from database.database import SessionLocal
from database.ipo_repository import (
    get_ipo_by_id,
    get_financial_metrics,
)


session = SessionLocal()

try:

    ipo = get_ipo_by_id(
        session,
        "cultfit-2026",
    )

    if ipo is None:
        print(
            "CULT.FIT IPO not found."
        )

    else:

        metrics = get_financial_metrics(
            session,
            ipo.id,
        )

        print(
            "CULT.FIT FINANCIAL METRICS:"
        )

        for metric in metrics:
            print(
                metric.metric_name,
                metric.period,
                metric.value,
                metric.unit,
                "document_id=",
                metric.source_document_id,
                "page=",
                metric.page_number,
            )

finally:
    session.close()