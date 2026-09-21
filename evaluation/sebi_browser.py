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
        Find the SEBI search input without relying
        on one fragile CSS selector.
        """

        inputs = page.locator(
            "input"
        )

        for index in range(
            inputs.count()
        ):
            element = inputs.nth(
                index
            )

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

            combined = (
                f"{placeholder} "
                f"{aria_label} "
                f"{name}"
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

        # Fallback: first visible text input.
        for index in range(
            inputs.count()
        ):
            element = inputs.nth(
                index
            )

            if element.is_visible():
                input_type = (
                    element.get_attribute(
                        "type"
                    )
                    or "text"
                ).lower()

                if input_type == "text":
                    return element

        raise RuntimeError(
            "Could not locate the SEBI search input."
        )

    def _search(
        self,
        page: Page,
        company_name: str,
    ) -> None:
        """
        Search SEBI for a company.
        """

        search_input = (
            self._find_search_input(
                page
            )
        )

        search_input.fill(
            company_name
        )

        # Find the GO button near the search controls.
        buttons = page.locator(
            "button, input[type='button'], "
            "input[type='submit']"
        )

        for index in range(
            buttons.count()
        ):
            button = buttons.nth(
                index
            )

            if not button.is_visible():
                continue

            text = (
                button.inner_text()
                if button.evaluate(
                    "(el) => el.tagName"
                )
                == "BUTTON"
                else (
                    button.get_attribute(
                        "value"
                    )
                    or ""
                )
            )

            if text.strip().upper() == "GO":
                button.click()
                page.wait_for_load_state(
                    "networkidle"
                )
                return

        raise RuntimeError(
            "Could not locate the SEBI search button."
        )

    def _extract_results(
    self,
    page: Page,
    company_name: str,
    ) -> list[DiscoveredSEBIDocument]:
        """
        Extract DRHP/RHP filing links from the
        currently loaded SEBI results page.
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

        links = page.locator(
            "a"
        )

        print(
            f"DEBUG: found {links.count()} links"
        )

        for index in range(
            links.count()
        ):
            debug_link = links.nth(index)

            try:
                title = debug_link.inner_text().strip()
                href = debug_link.get_attribute("href")

                if (
                    "CULT" in title.upper()
                    or (
                        href
                        and "cult" in href.lower()
                    )
                ):
                    print(
                        "DEBUG CULT LINK:"
                    )
                    print(
                        "TITLE:",
                        repr(title),
                    )
                    print(
                        "HREF:",
                        repr(href),
                    )
            except Exception as exc:
                print(
                    "DEBUG LINK ERROR:",
                    exc,
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

            if not title or not href:
                continue

            normalized_title = (
                " ".join(
                    title
                    .upper()
                    .split()
                )
            )

            # Company must appear in the link title.
            if target not in normalized_title:
                continue

            # Ignore abridged prospectus links.
            if "ABRIDGED PROSPECTUS" in normalized_title:
                continue

            if "DRHP" in normalized_title:
                document_type = "DRHP"

            elif (
                "RHP" in normalized_title
                and "ABRIDGED" not in normalized_title
            ):
                document_type = "RHP"

            else:
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
        Debug version of SEBI discovery.
        """

        print("=== DISCOVER() STARTED ===")
        print("Company:", company_name)

        with sync_playwright() as playwright:

            print("=== PLAYWRIGHT STARTED ===")

            browser = playwright.chromium.launch(
                headless=self.headless
            )

            print("=== BROWSER STARTED ===")

            page = browser.new_page()

            try:
                print(
                    "Opening:",
                    SEBI_PUBLIC_ISSUES_URL,
                )

                response = page.goto(
                    SEBI_PUBLIC_ISSUES_URL,
                    wait_until="domcontentloaded",
                    timeout=30_000,
                )

                print(
                    "Navigation status:",
                    response.status
                    if response
                    else None,
                )

                print(
                    "Current URL:",
                    page.url,
                )

                print(
                    "Page title:",
                    page.title(),
                )

                body = page.locator(
                    "body"
                ).inner_text()

                print(
                    "BODY LENGTH:",
                    len(body),
                )

                print(
                    "BODY PREVIEW:"
                )

                print(
                    body[:2000]
                )

                links = page.locator(
                    "a"
                )

                print(
                    "TOTAL LINKS:",
                    links.count(),
                )

                return []

            finally:
                browser.close()

                print(
                    "=== BROWSER CLOSED ==="
                )