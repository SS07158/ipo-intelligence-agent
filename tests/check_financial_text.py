from ingestion.sebi.document_parser import (
    parse_document,
)


PDF_PATH = (
    "data/raw/nse/"
    "cultfit_limited/"
    "Registration_07072026083041_DRHP.pdf"
)


pages = parse_document(
    PDF_PATH
)


for page in pages:

    text = page.get(
        "text",
        "",
    )

    if not text:
        continue

    lines = text.splitlines()

    for index, line in enumerate(lines):

        normalized = (
            " ".join(
                line.split()
            ).lower()
        )

        # Look for the actual row label rather than
        # a sentence mentioning the financial statement.
        if (
            normalized
            in {
                "profit/(loss) for the year",
                "profit / (loss) for the year",
                "profit (loss) for the year",
                "profit for the year",
                "loss for the year",
            }
        ):

            start = max(
                0,
                index - 15,
            )

            end = min(
                len(lines),
                index + 25,
            )

            page_number = (
                page.get("page_number")
                or page.get("page")
            )

            print()
            print(
                "=" * 100
            )

            print(
                "PAGE:",
                page_number,
            )

            print(
                "MATCH LINE:",
                index,
            )

            print(
                "=" * 100
            )

            for line_number in range(
                start,
                end,
            ):

                print(
                    f"{line_number}: "
                    f"{lines[line_number]}"
                )

            raise SystemExit