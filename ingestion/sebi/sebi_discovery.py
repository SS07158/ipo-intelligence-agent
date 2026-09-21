from html.parser import HTMLParser
from urllib.request import Request, urlopen

from ingestion.sebi.discovery import (
    DiscoveredSEBIDocument,
)



class SEBIListingParser(HTMLParser):
    """
    Parse SEBI public-issue listing HTML.

    We intentionally keep this parser independent from
    HTTP/network logic so it is easy to test.
    """

    def __init__(self):
        super().__init__()

        self.current_date: str | None = None
        self.current_href: str | None = None
        self.current_text: list[str] = []

        self.documents: list[
            DiscoveredSEBIDocument
        ] = []

        self._inside_link = False

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:

        attributes = dict(attrs)

        if tag == "a":

            href = attributes.get(
                "href"
            )

            if href:
                self.current_href = href

            self.current_text = []
            self._inside_link = True

    def handle_data(
        self,
        data: str,
    ) -> None:

        text = data.strip()

        if not text:
            return

        if self._inside_link:
            self.current_text.append(
                text
            )

    def handle_endtag(
        self,
        tag: str,
    ) -> None:

        if tag != "a":
            return

        if not self._inside_link:
            return

        title = " ".join(
            self.current_text
        ).strip()

        href = self.current_href

        self._inside_link = False
        self.current_text = []
        self.current_href = None

        if not href or not title:
            return

        normalized = title.upper()

        if "DRHP" not in normalized:
            return

        # Avoid picking the companion
        # "Draft Abridged Prospectus" link.
        if (
            "ABRIDGED PROSPECTUS"
            in normalized
        ):
            return

        self.documents.append(
            DiscoveredSEBIDocument(
                company_name=title
                    .replace(
                        " - DRHP",
                        "",
                    )
                    .strip(),
                document_type="DRHP",
                detail_url=href,
                discovered_date=(
                    self.current_date
                ),
            )
        )

def find_company(
    documents: list[DiscoveredSEBIDocument],
    company_name: str,
    ) -> list[DiscoveredSEBIDocument]:
        """
        Find discovered documents matching a company name.
        """

        target = (
            company_name
            .strip()
            .upper()
        )

        return [
            document
            for document in documents
            if document.company_name.upper()
            == target
        ]   


SEBI_PUBLIC_ISSUES_URL = (
    "https://www.sebi.gov.in/"
    "sebiweb/home/HomeAction.do"
    "?doListing=yes"
    "&sid=3"
    "&smid=10"
    "&ssid=15"
)


def fetch_listing_html(
    url: str = SEBI_PUBLIC_ISSUES_URL,
) -> str:
    """
    Fetch the SEBI public-issues listing page.
    """

    request = Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "Chrome/151.0 Safari/537.36"
            )
        },
    )

    with urlopen(
        request,
        timeout=30,
    ) as response:

        return response.read().decode(
            "utf-8",
            errors="replace",
        )


def discover_documents(
    company_name: str,
) -> list[DiscoveredSEBIDocument]:
    """
    Discover matching DRHP documents from the
    currently accessible SEBI public-issues listing.
    """

    html = fetch_listing_html()

    parser = SEBIListingParser()

    parser.feed(html)

    return find_company(
        parser.documents,
        company_name,
    )

    