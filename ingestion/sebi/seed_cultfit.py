from ingestion.ipo_config import IPOConfig
from ingestion.seed_ipo import seed_ipo


CULTFIT_CONFIG = IPOConfig(
    ipo_id="cultfit-2026",
    company_name="CULT.FIT LIMITED",
    fresh_issue=950.0,
    offer_for_sale_shares=178_609_200,
    document_id="cultfit-drhp-2026",
    document_type="DRHP",
    document_title="CULT.FIT LIMITED - DRHP",
    source="SEBI",
    source_url=(
        "https://www.sebi.gov.in/filings/public-issues/"
        "jul-2026/cult-fit-limited-drhp_102714.html"
    ),
    local_path=(
        "data/raw/sebi/cultfit/"
        "cultfit_drhp.pdf"
    ),
)


FINANCIAL_DATA = [
    {
        "metric_name": "revenue_from_operations",
        "period": "FY2024",
        "value": 9266.62,
        "unit": "INR million",
    },
    {
        "metric_name": "revenue_from_operations",
        "period": "FY2025",
        "value": 12155.36,
        "unit": "INR million",
    },
    {
        "metric_name": "revenue_from_operations",
        "period": "FY2026",
        "value": 17206.06,
        "unit": "INR million",
    },
]


def main() -> None:
    seed_ipo(
        CULTFIT_CONFIG,
        FINANCIAL_DATA,
    )


if __name__ == "__main__":
    main()