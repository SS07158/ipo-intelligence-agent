from ingestion.download import (
    download_offer_document,
)


URL = (
    "https://nsearchives.nseindia.com/"
    "corporate/Cultfit.zip"
)


result = download_offer_document(
    URL,
    "data/raw/sebi/cultfit/"
    "cultfit_drhp.pdf",
    "DRHP",
)

print(
    "RESULT:"
)

print(
    result
)