import logging
from typing import Dict, List, Optional

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

logger = logging.getLogger(__name__)


class AIService:
    """AI service for text processing"""

    def __init__(self):
        self.summarizer = None
        self.vectorizer = TfidfVectorizer(max_features=100, stop_words="english")

    def load_summarizer(self):
        """Load summarization model"""
        try:
            from transformers import pipeline
            if self.summarizer is None:
                logger.info("Loading summarization model")
                self.summarizer = pipeline(
                    "summarization",
                    model="facebook/bart-large-cnn"
                )
            return self.summarizer
        except ImportError:
            logger.warning("Transformers not available, using extractive summarization")
            return None
        except Exception as e:
            logger.warning(f"Could not load summarization model: {e}")
            return None

    def summarize_text(
        self,
        text: str,
        max_length: int = 150,
        min_length: int = 30
    ) -> Optional[str]:
        """Summarize text"""
        if not text or len(text.strip()) < 100:
            return text

        try:
            summarizer = self.load_summarizer()

            if summarizer:
                # Abstractive summarization with transformers
                summary = summarizer(
                    text,
                    max_length=max_length,
                    min_length=min_length,
                    do_sample=False
                )
                return summary[0]["summary_text"]
            else:
                # Extractive summarization fallback
                return self._extractive_summarize(text, max_sentences=3)

        except Exception as e:
            logger.error(f"Error summarizing text: {e}")
            return self._extractive_summarize(text, max_sentences=3)

    def _extractive_summarize(self, text: str, max_sentences: int = 3) -> str:
        """Extractive summarization based on TF-IDF"""
        try:
            # Simple implementation without nltk
            sentences = [s.strip() for s in text.split(".") if s.strip()]
            if len(sentences) <= max_sentences:
                return text

            # Calculate sentence importance by length (simplified approach)
            sentence_scores = [len(sentence) for sentence in sentences]

            # Select top sentences
            top_sentence_indices = np.argsort(sentence_scores)[-max_sentences:][::-1]
            top_sentences = [sentences[i] for i in sorted(top_sentence_indices)]

            return ". ".join(top_sentences) + "."
        except Exception as e:
            logger.error(f"Error in extractive summarization: {e}")
            if len(text) > 500:
                return text[:500] + "..."
            return text

    def extract_keywords(self, text: str, num_keywords: int = 5) -> List[str]:
        """Extract keywords from text"""
        if not text:
            return []

        try:
            # Simple approach based on TF-IDF
            stop_words = [
                "the", "a", "an", "and", "or", "but", "in", "on", "at", "to",
                "for", "of", "with", "by", "это", "как", "так", "и", "в", "над",
                "к", "до", "не", "на", "но", "за", "то", "с", "ли", "а", "во",
                "от", "со", "для", "о", "же", "ну", "вы", "бы", "что", "кто",
                "он", "она"
            ]

            vectorizer = TfidfVectorizer(
                max_features=num_keywords * 2,
                stop_words=stop_words,
                ngram_range=(1, 2)
            )

            tfidf_matrix = vectorizer.fit_transform([text])
            feature_names = vectorizer.get_feature_names_out()
            scores = tfidf_matrix.toarray().flatten()

            # Select top keywords
            top_indices = scores.argsort()[-num_keywords:][::-1]
            keywords = [feature_names[i] for i in top_indices]

            return keywords[:num_keywords]

        except Exception as e:
            logger.error(f"Error extracting keywords: {e}")
            return []

    def categorize_document(
        self,
        text: str,
        categories: Optional[List[str]] = None
    ) -> Dict[str, float]:
        """Categorize document into predefined categories"""
        if categories is None:
            categories = [
                "technical",
                "scientific",
                "news",
                "educational",
                "business"
            ]

        # Simple classifier based on keywords
        category_keywords = {
            "technical": [
                "programming", "code", "algorithm", "system", "technology"
            ],
            "scientific": [
                "research", "experiment", "theory", "analysis", "method"
            ],
            "news": [
                "news", "event", "incident", "message", "announcement"
            ],
            "educational": [
                "learning", "course", "student", "teacher", "textbook"
            ],
            "business": [
                "company", "market", "sales", "profit", "investment"
            ]
        }

        text_lower = text.lower()
        scores = {}

        for category, keywords in category_keywords.items():
            if category in categories:
                score = sum(1 for keyword in keywords if keyword in text_lower)
                scores[category] = score / len(keywords) if keywords else 0

        return scores

    def find_similar_documents(
        self,
        target_text: str,
        documents_data: List[Dict],
        top_k: int = 5
    ) -> List[Dict]:
        """Find similar documents based on keywords"""
        if not documents_data:
            return []

        # Simple implementation based on keyword similarity
        target_keywords = set(self.extract_keywords(target_text, 10))

        scored_docs = []
        for doc in documents_data:
            doc_keywords = set(self.extract_keywords(
                doc.get("content", "") or doc.get("title", ""),
                10
            ))

            if target_keywords or doc_keywords:
                intersection = len(target_keywords & doc_keywords)
                union = len(target_keywords | doc_keywords)
                similarity = intersection / union if union > 0 else 0
            else:
                similarity = 0

            scored_docs.append({
                "id": doc.get("id"),
                "title": doc.get("title", ""),
                "similarity": similarity,
                "file_type": doc.get("file_type")
            })

        # Sort by similarity
        scored_docs.sort(key=lambda x: x["similarity"], reverse=True)
        return scored_docs[:top_k]

    def cluster_documents(
        self,
        documents_data: List[Dict],
        num_clusters: int = 3
    ) -> List[Dict]:
        """Cluster documents by topics"""
        if not documents_data or len(documents_data) < num_clusters:
            return [{
                "cluster_id": 0,
                "documents": documents_data,
                "topic": "All documents"
            }]

        # Simple clustering (round-robin distribution)
        clusters = []
        for i in range(num_clusters):
            clusters.append({
                "cluster_id": i,
                "documents": [],
                "topic": f"Topic {i + 1}"
            })

        # Distribute documents (simple round-robin)
        for idx, doc in enumerate(documents_data):
            cluster_idx = idx % num_clusters
            clusters[cluster_idx]["documents"].append(doc)

        return clusters


# Global service instance
ai_service = AIService()
