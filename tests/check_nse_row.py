from playwright.sync_api import sync_playwright


URL = (
    "https://www.nseindia.com/"
    "companies-listing/"
    "corporate-filings-offer-documents"
)


with sync_playwright() as playwright:

    browser = playwright.chromium.launch(
        headless=True
    )

    page = browser.new_page()

    try:

        page.goto(
            URL,
            wait_until="domcontentloaded",
            timeout=30_000,
        )

        page.wait_for_timeout(
            5_000
        )

        body = page.locator(
            "body"
        ).inner_text()

        print(
            "CULT.FIT PRESENT:",
            "CULT.FIT" in body.upper(),
        )

        print(
            "\n=== TABLES ==="
        )

        tables = page.locator(
            "table"
        )

        print(
            "TABLE COUNT:",
            tables.count(),
        )

        for index in range(
            tables.count()
        ):

            table = tables.nth(
                index
            )

            text = table.inner_text()

            if (
                "CULT.FIT"
                in text.upper()
            ):

                print(
                    "\n=== CULT.FIT TABLE ==="
                )

                print(
                    "TABLE INDEX:",
                    index,
                )

                print(
                    text[:5000]
                )

                print(
                    "\n=== HTML ==="
                )

                print(
                    table.evaluate(
                        "(el) => el.outerHTML"
                    )
                )

    finally:

        browser.close()