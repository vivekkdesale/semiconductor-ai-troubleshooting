from qdrant_client import QdrantClient, models

from semiconductor.config import Settings


class KnowledgeVectors:
    def __init__(self, settings: Settings):
        self.client = QdrantClient(url=settings.qdrant_url)
        self.collection = settings.qdrant_collection

    def ensure_collection(self, vector_size: int = 384) -> None:
        if not self.client.collection_exists(self.collection):
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=models.VectorParams(
                    size=vector_size, distance=models.Distance.COSINE
                ),
            )
