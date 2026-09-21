from sqlalchemy import text

from database.database import engine


COLUMNS = {
    "acquisition_source": (
        "VARCHAR(100)"
    ),
    "document_url": (
        "VARCHAR(1000)"
    ),
}


def main() -> None:

    with engine.begin() as connection:

        for column_name, column_type in (
            COLUMNS.items()
        ):

            result = connection.execute(
                text(
                    "SELECT name "
                    "FROM pragma_table_info("
                    "'ipo_documents'"
                    ") "
                    "WHERE name = :name"
                ),
                {
                    "name": column_name
                },
            )

            exists = (
                result.first()
                is not None
            )

            if exists:
                print(
                    f"{column_name}: "
                    "already exists"
                )
                continue

            connection.execute(
                text(
                    "ALTER TABLE ipo_documents "
                    f"ADD COLUMN {column_name} "
                    f"{column_type}"
                )
            )

            print(
                f"{column_name}: added"
            )


if __name__ == "__main__":
    main()