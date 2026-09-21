from sqlalchemy import text

from database.database import engine


def get_columns(connection) -> set[str]:
    rows = connection.execute(
        text(
            "PRAGMA table_info(ipo_documents)"
        )
    ).fetchall()

    return {
        row[1]
        for row in rows
    }


def add_column_if_missing(
    connection,
    columns: set[str],
    column_name: str,
    column_sql: str,
) -> None:

    if column_name in columns:
        print(
            f"{column_name} already exists."
        )
        return

    connection.execute(
        text(
            f"""
            ALTER TABLE ipo_documents
            ADD COLUMN {column_sql}
            """
        )
    )

    columns.add(
        column_name
    )

    print(
        f"Added {column_name}."
    )


def migrate() -> None:

    with engine.begin() as connection:

        columns = get_columns(
            connection
        )

        add_column_if_missing(
            connection,
            columns,
            "indexed_at",
            "indexed_at DATETIME",
        )

        add_column_if_missing(
            connection,
            columns,
            "version",
            "version VARCHAR",
        )

        add_column_if_missing(
            connection,
            columns,
            "published_at",
            "published_at DATETIME",
        )



if __name__ == "__main__":
    migrate()