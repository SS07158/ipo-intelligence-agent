from typing import Any

import requests

from ingestion.nse.offer_documents import (
    NSEDocument,
    NSEOfferDocumentSource,
)


NSE_OFFER_DOCS_API = (
    "https://www.nseindia.com/api/"
    "corporates/offerdocs"
)


class NSEOfferDocumentDiscovery:
    """
    Discover IPO offer documents from NSE's
    official offer-document API.
    """

    def __init__(
        self,
        timeout: int = 30,
    ):
        self.timeout = timeout

        self.session = requests.Session()

        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 "
                    "(KHTML, like Gecko) "
                    "Chrome/151.0 Safari/537.36"
                ),
                "Accept": (
                    "application/json, "
                    "text/plain, */*"
                ),
                "Referer": (
                    "https://www.nseindia.com/"
                ),
                "Accept-Language": (
                    "en-US,en;q=0.9"
                ),
            }
        )

    def _get_data(
        self,
        company_name: str,
    ) -> list[dict[str, Any]]:
        """
        Fetch offer-document records from NSE.
        """

        response = self.session.get(
            NSE_OFFER_DOCS_API,
            params={
                "index": "equities",
                "company": company_name,
            },
            timeout=self.timeout,
        )

        response.raise_for_status()

        data = response.json()

        if not isinstance(
            data,
            list,
        ):
            raise RuntimeError(
                "Unexpected NSE response format. "
                "Expected a list."
            )

        return data

    @staticmethod
    def _normalize(
        value: str | None,
    ) -> str:
        if value is None:
            return ""

        return (
            " ".join(
                value.strip()
                .upper()
                .split()
            )
        )

    def _find_record(
        self,
        records: list[dict[str, Any]],
        company_name: str,
    ) -> dict[str, Any] | None:
        """
        Find the company record in NSE's response.
        """

        target = self._normalize(
            company_name
        )

        for record in records:

            if not isinstance(
                record,
                dict,
            ):
                continue

            company = self._normalize(
                record.get("company")
            )

            if company == target:
                return record

        return None

    def find_document(
        self,
        company_name: str,
        document_type: str,
    ) -> NSEDocument | None:
        """
        Find a DRHP or RHP document for a company.

        NSE exposes separate fields for DRHP and RHP.
        """

        document_type = (
            document_type
            .strip()
            .upper()
        )

        if document_type not in {
            "DRHP",
            "RHP",
        }:
            raise ValueError(
                "document_type must be "
                "DRHP or RHP."
            )

        records = self._get_data(
            company_name
        )

        record = self._find_record(
            records,
            company_name,
        )

        if record is None:
            return None

        source = (
            NSEOfferDocumentSource()
        )

        if document_type == "DRHP":

            url = record.get(
                "drhpAttach"
            )

            date = record.get(
                "drhpDate"
            )

            if not url:
                return None

            return source.resolve_document(
                company_name=company_name,
                document_type="DRHP",
                document_url=url,
                document_date=date,
            )

        # RHP
        url = record.get(
            "rhpAttach"
        )

        date = record.get(
            "rhpDate"
        )

        if not url:
            return None

        return source.resolve_document(
            company_name=company_name,
            document_type="RHP",
            document_url=url,
            document_date=date,
        )

    def get_company_record(
    self,
    company_name: str,
    ) -> dict[str, Any] | None:
        """
        Return the raw NSE company record.
        """

        records = self._get_data(
            company_name
        )

        return self._find_record(
            records,
            company_name,
        )