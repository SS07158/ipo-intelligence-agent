from sqlalchemy import select

from database.database import SessionLocal
from database.models import IPODocument, IPO

from ingestion.sebi.document_config import (
    SEBIDocumentConfig,
)

from datetime import datetime, timezone


def register_document(
    config: SEBIDocumentConfig,
) -> IPODocument:
    """
    Register a SEBI IPO document in the SQL database.

    Returns an existing document when the document_id
    is already registered.
    """

    session = SessionLocal()

    try:
        # Find the IPO using the canonical IPO identifier.
        statement = select(IPO).where(
            IPO.ipo_id == config.ipo_id
        )

        ipo = session.scalar(
            statement
        )

        if ipo is None:
            raise ValueError(
                f"IPO not found for document "
                f"'{config.document_id}'."
            )

        # Check whether this document already exists.
        statement = select(
            IPODocument
        ).where(
            IPODocument.document_id
            == config.document_id
        )

        document = session.scalar(
            statement
        )

        if document is not None:
            return document

        document = IPODocument(
            document_id=config.document_id,
            ipo_id=ipo.id,
            document_type=config.document_type,
            title=(
                f"{config.company_name} - "
                f"{config.document_type}"
            ),
            source=config.source,
            source_url=config.source_url,
            local_path=config.local_path,
            version = config.version,
            published_at = config.published_at
        )

        session.add(
            document
        )

        session.commit()
        session.refresh(
            document
        )

        return document

    finally:
        session.close()

def mark_document_indexed(
    document_id: str,
) -> None:
    """
    Mark an IPO document as successfully indexed.
    """

    session = SessionLocal()

    try:
        document = session.query(
            IPODocument
        ).filter(
            IPODocument.document_id
            == document_id
        ).first()

        if document is None:
            raise ValueError(
                f"Document not found: "
                f"{document_id}"
            )

        document.indexed_at = (
            datetime.now(timezone.utc)
        )

        session.commit()

    finally:
        session.close()

def is_document_indexed(
    document_id: str,
) -> bool:
    """
    Return True when the document has already
    been successfully indexed.
    """

    session = SessionLocal()

    try:
        document = session.query(
            IPODocument
        ).filter(
            IPODocument.document_id
            == document_id
        ).first()

        return (
            document is not None
            and document.indexed_at is not None
        )

    finally:
        session.close()


def document_exists(
    document_id: str,
) -> bool:
    session = SessionLocal()

    try:
        document = session.query(
            IPODocument
        ).filter(
            IPODocument.document_id
            == document_id
        ).first()

        return document is not None

    finally:
        session.close()