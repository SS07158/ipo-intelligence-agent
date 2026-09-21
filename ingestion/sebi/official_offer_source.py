from urllib.parse import urljoin

from playwright.sync_api import sync_playwright


MORGAN_STANLEY_OFFER_DOCS_URL = (
    "https://www.morganstanley.com/"
    "indiaofferdocuments/document1"
)


class OfferDocumentSource:
    """
    Discover IPO offer documents from the
    official book-running lead manager page.
    """

    def __init__(
        self,
        headless: bool = True,
    ):
        self.headless = headless

    def find_document(
        self,
        company_name: str,
        document_type: str,
    ) -> str | None:
        """
        Find a specific offer document.

        Example:
            CULT.FIT LIMITED + DRHP
        """

        target_company = (
            company_name
            .strip()
            .upper()
        )

        target_type = (
            document_type
            .strip()
            .upper()
        )

        with sync_playwright() as playwright:

            browser = playwright.chromium.launch(
                headless=self.headless
            )

            page = browser.new_page()

            try:
                page.goto(
                    MORGAN_STANLEY_OFFER_DOCS_URL,
                    wait_until="domcontentloaded",
                    timeout=30_000,
                )

                page.wait_for_timeout(
                    1_000
                )

                links = page.locator(
                    "a"
                )

                for index in range(
                    links.count()
                ):

                    link = links.nth(
                        index
                    )

                    if not link.is_visible():
                        continue

                    text = (
                        link.inner_text()
                        .strip()
                    )

                    href = (
                        link.get_attribute(
                            "href"
                        )
                    )

                    if not href:
                        continue

                    normalized = (
                        " ".join(
                            text.upper().split()
                        )
                    )

                    if target_company not in normalized:
                        continue

                    if (
                        target_type == "DRHP"
                        and "DRAFT RED HERRING PROSPECTUS"
                        not in normalized
                    ):
                        continue

                    if (
                        target_type == "RHP"
                        and "RED HERRING PROSPECTUS"
                        not in normalized
                    ):
                        continue

                    return urljoin(
                        MORGAN_STANLEY_OFFER_DOCS_URL,
                        href,
                    )

                return None

            finally:
                browser.close()