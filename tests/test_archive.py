from pathlib import Path
from zipfile import ZipFile

import pytest

from ingestion.archive import (
    ArchiveExtractionError,
    extract_document_from_zip,
)


def test_extract_drhp_pdf(
    tmp_path: Path,
):

    zip_path = (
        tmp_path
        / "cultfit.zip"
    )

    with ZipFile(
        zip_path,
        "w",
    ) as archive:

        archive.writestr(
            "Cultfit_DRHP.pdf",
            b"%PDF-1.7\ndrhp content",
        )

        archive.writestr(
            "readme.txt",
            b"metadata",
        )

    output = (
        extract_document_from_zip(
            zip_path,
            tmp_path / "output",
            "DRHP",
        )
    )

    assert output.exists()

    assert (
        output.name
        == "Cultfit_DRHP.pdf"
    )

    assert (
        output.read_bytes()
        .startswith(b"%PDF")
    )


def test_no_pdf_in_zip(
    tmp_path: Path,
):

    zip_path = (
        tmp_path
        / "empty.zip"
    )

    with ZipFile(
        zip_path,
        "w",
    ) as archive:

        archive.writestr(
            "readme.txt",
            b"no pdf",
        )

    with pytest.raises(
        ArchiveExtractionError
    ):

        extract_document_from_zip(
            zip_path,
            tmp_path / "output",
            "DRHP",
        )