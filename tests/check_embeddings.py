from app.retrieval.embedding_service import EmbeddingService


service = EmbeddingService()

texts = [
    "The company faces risks related to competition.",
    "The company operates fitness centers across India.",
    "The company intends to use proceeds for business purposes.",
]

embeddings = service.embed_documents(texts)

print("Number of embeddings:", len(embeddings))
print("Embedding dimension:", len(embeddings[0]))

query = service.embed_query(
    "What are the risks from competition?"
)

print("Query embedding dimension:", len(query))