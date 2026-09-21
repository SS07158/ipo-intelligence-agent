from ingestion.download import (
    download_document,
)


URL = (
    "https://nsearchives.nseindia.com/"
    "corporate/"
    "Registration_07072026083041_DRHP.pdf"
)


result = download_document(
    URL,
    "data/raw/sebi/cultfit/"
    "cultfit_drhp_nse.pdf",
)

print(
    "Downloaded:"
)

print(
    result
)