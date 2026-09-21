from sqlalchemy import delete

from database.database import SessionLocal
from database.models import FinancialMetric


session = SessionLocal()

try:

    statement = delete(
        FinancialMetric
    ).where(
        FinancialMetric.metric_name
        == "__test_metric__"
    )

    result = session.execute(
        statement
    )

    session.commit()

    print(
        "Deleted test metrics:",
        result.rowcount,
    )

finally:

    session.close()