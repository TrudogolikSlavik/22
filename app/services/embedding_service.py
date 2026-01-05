import json
import logging
import os
from datetime import datetime
from typing import List, Tuple

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session

from app.models.document import Document

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for document embeddings and semantic search"""

    def __init__(self):
        self.model = None
        self.index = None
        self.document_ids = []
        self.model_name = "sentence-transformers/all-MiniLM-L6-v2"

    def load_model(self):
        """Load embedding model"""
        if self.model is None:
            logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
        return self.model

    def create_embeddings(self, texts: List[str]) -> np.ndarray:
        """Create embeddings for list of texts"""
        model = self.load_model()
        embeddings = model.encode(texts, normalize_embeddings=True)
        return embeddings

    def create_index(self, embeddings: np.ndarray):
        """Create FAISS index for embeddings"""
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)  # Inner Product (cosine similarity)
        self.index.add(embeddings.astype("float32"))

    def semantic_search(self, query: str, k: int = 10) -> List[Tuple[int, float]]:
        """Perform semantic search for query"""
        if self.index is None or len(self.document_ids) == 0:
            return []

        model = self.load_model()
        query_embedding = model.encode([query], normalize_embeddings=True)

        # Search in index
        scores, indices = self.index.search(query_embedding.astype("float32"), k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.document_ids):
                results.append((self.document_ids[idx], float(score)))

        return results

    def build_index_from_documents(self, db: Session, user_id: int):
        """Build index from user documents"""
        documents = db.query(Document).filter(
            Document.owner_id == user_id,
            Document.content.isnot(None),
            Document.content != ""
        ).all()

        if not documents:
            logger.warning(f"No documents with content found for user {user_id}")
            return

        texts = []
        self.document_ids = []

        for doc in documents:
            # Combine title and content for better search
            text = f"{doc.title}. {doc.content}" if doc.content else doc.title
            texts.append(text)
            self.document_ids.append(doc.id)

        logger.info(f"Building index for {len(texts)} documents")
        embeddings = self.create_embeddings(texts)
        self.create_index(embeddings)

        # Save index
        self.save_index(user_id)

    def save_index(self, user_id: int):
        """Save index and mapping for user"""
        if self.index is None:
            return

        index_dir = f"data/indices/user_{user_id}"
        os.makedirs(index_dir, exist_ok=True)

        # Save FAISS index
        faiss.write_index(self.index, f"{index_dir}/index.faiss")

        # Save mapping document_id -> index
        with open(f"{index_dir}/mapping.json", "w") as f:
            json.dump({
                "document_ids": self.document_ids,
                "created_at": datetime.now().isoformat(),
                "model": self.model_name
            }, f)

    def load_index(self, user_id: int) -> bool:
        """Load index and mapping for user"""
        index_dir = f"data/indices/user_{user_id}"
        index_path = f"{index_dir}/index.faiss"
        mapping_path = f"{index_dir}/mapping.json"

        if not os.path.exists(index_path) or not os.path.exists(mapping_path):
            return False

        try:
            self.index = faiss.read_index(index_path)

            with open(mapping_path) as f:
                mapping = json.load(f)
                self.document_ids = mapping["document_ids"]

            logger.info(
                f"Loaded index for user {user_id} "
                f"with {len(self.document_ids)} documents"
            )
            return True
        except Exception as e:
            logger.error(f"Error loading index for user {user_id}: {e}")
            return False


# Global service instance
embedding_service = EmbeddingService()
