from pathlib import Path
from zipfile import ZipFile, BadZipFile


class ArchiveExtractionError(Exception):
    """
    Raised when an archive cannot be safely processed.
    """


def extract_document_from_zip(
    zip_path: str | Path,
    destination_dir: str | Path,
    document_type: str,
) -> Path:
    """
    Extract the requested DRHP/RHP PDF from a ZIP archive.

    Returns:
        Path to the extracted PDF.
    """

    zip_path = Path(zip_path)

    destination_dir = Path(
        destination_dir
    )

    destination_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

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
            "document_type must be DRHP or RHP."
        )

    if not zip_path.exists():
        raise ArchiveExtractionError(
            f"ZIP file does not exist: {zip_path}"
        )

    try:
        with ZipFile(
            zip_path,
            "r",
        ) as archive:

            members = archive.infolist()

            pdf_members = [
                member
                for member in members
                if (
                    not member.is_dir()
                    and member.filename.lower().endswith(
                        ".pdf"
                    )
                )
            ]

            if not pdf_members:
                raise ArchiveExtractionError(
                    "ZIP archive contains no PDF files."
                )

            target_members = [
                member
                for member in pdf_members
                if document_type
                in Path(
                    member.filename
                ).stem.upper()
            ]

            if not target_members:

                # If there is exactly one PDF, it is
                # reasonable to use it.
                if len(pdf_members) == 1:
                    target_members = pdf_members

                else:
                    raise ArchiveExtractionError(
                        f"Could not identify a "
                        f"{document_type} PDF in the archive."
                    )

            member = target_members[0]

            # Prevent path traversal when extracting.
            member_path = Path(
                member.filename
            )

            safe_filename = (
                member_path.name
            )

            output_path = (
                destination_dir
                / safe_filename
            )

            with archive.open(
                member
            ) as source, output_path.open(
                "wb"
            ) as destination:

                destination.write(
                    source.read()
                )

            return output_path

    except BadZipFile as exc:
        raise ArchiveExtractionError(
            "Downloaded file is not a valid ZIP archive."
        ) from exc