from sqlalchemy import text

from database.database import engine


INDEX_NAME = (
    "uq_financial_metric_ipo_metric_period"
)


def main() -> None:

    with engine.begin() as connection:

        # Remove duplicate records first, keeping
        # the lowest-id record for each logical metric.
        connection.execute(
            text(
                """
                DELETE FROM financial_metrics
                WHERE id NOT IN (
                    SELECT MIN(id)
                    FROM financial_metrics
                    GROUP BY ipo_id, metric_name, period
                )
                """
            )
        )

        # SQLite does not support adding a UNIQUE
        # constraint directly to an existing table
        # with ALTER TABLE, so create a unique index.
        connection.execute(
            text(
                f"""
                CREATE UNIQUE INDEX IF NOT EXISTS
                {INDEX_NAME}
                ON financial_metrics (
                    ipo_id,
                    metric_name,
                    period
                )
                """
            )
        )

        print(
            "Financial metric uniqueness enforced."
        )


if __name__ == "__main__":
    main()