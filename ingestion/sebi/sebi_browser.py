from urllib.parse import urljoin

from playwright.sync_api import (
    sync_playwright,
    Page,
)

from ingestion.sebi.discovery import (
    DiscoveredSEBIDocument,
)


SEBI_PUBLIC_ISSUES_URL = (
    "https://www.sebi.gov.in/"
    "sebiweb/home/HomeAction.do"
    "?doListing=yes"
    "&sid=3"
    "&smid=10"
    "&ssid=15"
)


class SEBIBrowserDiscovery:
    """
    Discover IPO documents from SEBI's public-issues
    web interface using Playwright.
    """

    def __init__(
        self,
        headless: bool = True,
    ):
        self.headless = headless

    def _find_search_input(
    self,
    page: Page,
    ):
        """
        Find the SEBI filing search input.
        """

        # Prefer an input associated with the search area.
        inputs = page.locator(
            "input"
        )

        for index in range(
            inputs.count()
        ):
            element = inputs.nth(
                index
            )

            if not element.is_visible():
                continue

            placeholder = (
                element.get_attribute(
                    "placeholder"
                )
                or ""
            ).lower()

            aria_label = (
                element.get_attribute(
                    "aria-label"
                )
                or ""
            ).lower()

            name = (
                element.get_attribute(
                    "name"
                )
                or ""
            ).lower()

            input_id = (
                element.get_attribute(
                    "id"
                )
                or ""
            ).lower()

            combined = (
                f"{placeholder} "
                f"{aria_label} "
                f"{name} "
                f"{input_id}"
            )

            if any(
                keyword in combined
                for keyword in (
                    "search",
                    "keyword",
                    "entity",
                    "title",
                )
            ):
                return element

        # Fallback: visible text input.
        visible_text_inputs = []

        for index in range(
            inputs.count()
        ):
            element = inputs.nth(
                index
            )

            if not element.is_visible():
                continue

            input_type = (
                element.get_attribute(
                    "type"
                )
                or "text"
            ).lower()

            if input_type in {
                "text",
                "search",
            }:
                visible_text_inputs.append(
                    element
                )

        if not visible_text_inputs:
            raise RuntimeError(
                "Could not locate the SEBI search input."
            )

        # The search field appears before the date
        # inputs on the current SEBI page.
        return visible_text_inputs[0]

    def _search(
    self,
    page: Page,
    company_name: str,
    ) -> None:
        """
        Search SEBI's Public Issues listing.
        """

        search_input = page.locator(
            "#search"
        )

        if not search_input.is_visible():
            raise RuntimeError(
                "SEBI search input is not visible."
            )

        search_input.fill(
            company_name
        )

        go_link = page.locator(
            "a.go_search",
            has_text="GO",
        )

        if go_link.count() == 0:
            raise RuntimeError(
                "Could not locate SEBI GO search control."
            )

        go_link.first.click()

        # The SEBI page uses JavaScript to update
        # the listing rather than a normal form submit.
        page.wait_for_timeout(
            3_000
        )

        # Wait until the search value remains populated
        # and the page has had a chance to update.
        try:
            page.wait_for_load_state(
                "networkidle",
                timeout=5_000,
            )
        except Exception:
            pass

    def _extract_results(
    self,
    page: Page,
    company_name: str,
    ) -> list[DiscoveredSEBIDocument]:
        """
        Extract matching DRHP/RHP links from the
        searched SEBI results.
        """

        target = (
            " ".join(
                company_name
                .strip()
                .upper()
                .split()
            )
        )

        documents = []

        # First check the page text.
        body_text = (
            page.locator("body")
            .inner_text()
            .upper()
        )

        if target not in body_text:
            return []

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

            title = (
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

            normalized_title = (
                " ".join(
                    title
                    .upper()
                    .split()
                )
            )

            # Ignore navigation/search controls.
            if (
                "javascript:"
                in href.lower()
            ):
                continue

            # We want actual DRHP/RHP links.
            if "DRHP" in normalized_title:
                document_type = "DRHP"

            elif (
                "RHP" in normalized_title
                and "ABRIDGED"
                not in normalized_title
            ):
                document_type = "RHP"

            else:
                continue

            # Exclude abridged prospectus.
            if "ABRIDGED" in normalized_title:
                continue

            # Keep likely IPO filing links.
            if (
                "public-issues"
                not in href.lower()
                and "filings"
                not in href.lower()
            ):
                continue

            documents.append(
                DiscoveredSEBIDocument(
                    company_name=company_name,
                    document_type=document_type,
                    detail_url=urljoin(
                        SEBI_PUBLIC_ISSUES_URL,
                        href,
                    ),
                )
            )

        return documents

    def discover(
    self,
    company_name: str,
    ) -> list[DiscoveredSEBIDocument]:
        """
        Search SEBI and return matching IPO documents.
        """

        with sync_playwright() as playwright:

            browser = playwright.chromium.launch(
                headless=self.headless
            )

            page = browser.new_page()

            try:
                page.goto(
                    SEBI_PUBLIC_ISSUES_URL,
                    wait_until="domcontentloaded",
                    timeout=30_000,
                )

                page.wait_for_timeout(
                    2_000
                )

                self._search(
                    page,
                    company_name,
                )

                return self._extract_results(
                    page,
                    company_name,
                )

            finally:
                browser.close()

    def extract_document_url(
    self,
    detail_url: str,
    document_type: str,
    ) -> str | None:
        """
        Extract the requested document URL from a
        SEBI detail page.

        Returns None when SEBI does not expose that
        specific document.
        """

        with sync_playwright() as playwright:

            browser = playwright.chromium.launch(
                headless=self.headless
            )

            page = browser.new_page()

            try:
                page.goto(
                    detail_url,
                    wait_until="domcontentloaded",
                    timeout=30_000,
                )

                page.wait_for_timeout(
                    1_500
                )

                links = page.locator(
                    "a"
                )

                target = (
                    document_type
                    .strip()
                    .upper()
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
                        .upper()
                    )

                    href = (
                        link.get_attribute(
                            "href"
                        )
                    )

                    if not href:
                        continue

                    # Ignore the generic site links.
                    if "SEBI_DATA" not in href.upper():
                        continue

                    # We need the actual requested document,
                    # not merely any PDF on the page.
                    if target in text:
                        return urljoin(
                            detail_url,
                            href,
                        )

                return None

            finally:
                browser.close()