from hashlib import sha256
from pathlib import Path
from urllib.request import Request, urlopen

from ingestion.archive import (
    extract_document_from_zip,
)


class DocumentDownloadError(Exception):
    """
    Raised when a document cannot be downloaded
    or fails validation.
    """


def _download_bytes(
    url: str,
    timeout: int = 60,
) -> tuple[bytes, str]:
    """
    Download raw bytes without assuming the file type.
    """

    if not url.strip():
        raise ValueError(
            "URL cannot be empty."
        )

    request = Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/151.0 Safari/537.36"
            )
        },
    )

    try:
        with urlopen(
            request,
            timeout=timeout,
        ) as response:

            status = response.status

            if status != 200:
                raise DocumentDownloadError(
                    f"HTTP status {status}"
                )

            content = response.read()

            content_type = (
                response.headers.get(
                    "Content-Type",
                    "",
                )
            )

    except Exception as exc:

        if isinstance(
            exc,
            DocumentDownloadError,
        ):
            raise

        raise DocumentDownloadError(
            f"Download failed: {exc}"
        ) from exc

    if not content:
        raise DocumentDownloadError(
            "Downloaded document is empty."
        )

    return (
        content,
        content_type,
    )


def _write_bytes(
    content: bytes,
    destination: str | Path,
) -> dict:
    """
    Write bytes to disk and return checksum metadata.
    """

    destination = Path(
        destination
    )

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    destination.write_bytes(
        content
    )

    checksum = sha256(
        content
    ).hexdigest()

    return {
        "local_path": str(
            destination
        ),
        "size_bytes": len(
            content
        ),
        "sha256": checksum,
    }


def _validate_pdf(
    content: bytes,
) -> None:
    """
    Validate PDF magic bytes.
    """

    if not content.startswith(
        b"%PDF"
    ):
        raise DocumentDownloadError(
            "Downloaded content does not appear "
            "to be a valid PDF."
        )


def _validate_zip(
    content: bytes,
) -> None:
    """
    Validate ZIP magic bytes.
    """

    # Standard ZIP signatures:
    # PK\x03\x04 = normal ZIP
    # PK\x05\x06 = empty ZIP
    # PK\x07\x08 = spanned ZIP
    valid_signatures = (
        b"PK\x03\x04",
        b"PK\x05\x06",
        b"PK\x07\x08",
    )

    if not content.startswith(
        valid_signatures
    ):
        raise DocumentDownloadError(
            "Downloaded content does not appear "
            "to be a valid ZIP archive."
        )


def download_document(
    url: str,
    destination: str | Path,
    timeout: int = 60,
) -> dict:
    """
    Download and validate a PDF document.
    """

    content, content_type = (
        _download_bytes(
            url,
            timeout,
        )
    )

    _validate_pdf(
        content
    )

    result = _write_bytes(
        content,
        destination,
    )

    return {
        "url": url,
        **result,
        "content_type": content_type,
        "archive_type": "direct",
    }


def download_offer_document(
    url: str,
    destination: str | Path,
    document_type: str,
    timeout: int = 60,
) -> dict:
    """
    Download an offer document that may be either
    a direct PDF or a ZIP archive containing the PDF.
    """

    destination = Path(
        destination
    )

    url_suffix = (
        url.split("?")[0]
        .lower()
    )

    is_zip = url_suffix.endswith(
        ".zip"
    )

    if is_zip:

        zip_destination = (
            destination.with_suffix(
                ".zip"
            )
        )

        content, content_type = (
            _download_bytes(
                url,
                timeout,
            )
        )

        _validate_zip(
            content
        )

        zip_result = _write_bytes(
            content,
            zip_destination,
        )

        extracted_pdf = (
            extract_document_from_zip(
                zip_destination,
                destination.parent,
                document_type,
            )
        )

        pdf_content = (
            extracted_pdf.read_bytes()
        )

        _validate_pdf(
            pdf_content
        )

        pdf_checksum = sha256(
            pdf_content
        ).hexdigest()

        return {
            "url": url,
            "local_path": str(
                extracted_pdf
            ),
            "size_bytes": len(
                pdf_content
            ),
            "sha256": pdf_checksum,
            "content_type": (
                "application/pdf"
            ),
            "archive_type": "zip",
            "archive_path": str(
                zip_destination
            ),
            "archive_size_bytes": (
                zip_result["size_bytes"]
            ),
            "archive_sha256": (
                zip_result["sha256"]
            ),
        }

    # Direct PDF case.
    content, content_type = (
        _download_bytes(
            url,
            timeout,
        )
    )

    _validate_pdf(
        content
    )

    result = _write_bytes(
        content,
        destination,
    )

    return {
        "url": url,
        **result,
        "content_type": content_type,
        "archive_type": "direct",
    }