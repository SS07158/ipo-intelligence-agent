import sqlite3

from app.retrieval.vector_store import VectorStore


db_path = r"C:\AI journey\Project\ipo_intelligent_agent\ipo_intelligence.db"
document_id = "sterlite-electric-drhp-2026"


# Get the source URL from SQLite
conn = sqlite3.connect(db_path)

query = """
SELECT source_url
FROM ipo_documents
WHERE document_id = ?
"""

url = conn.execute(query, (document_id,)).fetchone()[0]

conn.close()


# Initialize vector store
vector_store = VectorStore()

data = vector_store.collection.get(
    include=["metadatas"]
)


# Find chunks belonging to the document
ids = []
metadatas = []

for chunk_id, metadata in zip(
    data["ids"],
    data["metadatas"]
):
    if metadata.get("document_id") == document_id:
        ids.append(chunk_id)

        updated_metadata = {
            **metadata,
            "source_url": url,
        }

        metadatas.append(updated_metadata)


# Update metadata for matching chunks
vector_store.collection.update(
    ids=ids,
    metadatas=metadatas,
)


print("Updated chunks:", len(ids))
print("URL:", url)
