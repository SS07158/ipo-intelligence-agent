from sqlalchemy import inspect

from database.database import engine


def test_financial_metric_unique_index_exists():

    inspector = inspect(
        engine
    )

    indexes = inspector.get_indexes(
        "financial_metrics"
    )

    names = {
        index["name"]
        for index in indexes
    }

    assert (
        "uq_financial_metric_ipo_metric_period"
        in names
    )