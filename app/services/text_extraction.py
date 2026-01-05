import logging
from typing import Optional

logger = logging.getLogger(__name__)


class TextExtractionService:
    """Service for extracting text from files"""

    @staticmethod
    def extract_text_from_file(file_path: str) -> Optional[str]:
        """
        Extract text from file.

        In real project, add:
        - pdfplumber for PDF
        - python-docx for DOCX
        - Direct reading for txt files
        """
        try:
            # Simple implementation for text files
            if file_path.endswith(".txt"):
                with open(file_path, encoding="utf-8") as f:
                    return f.read()

            # For other formats return stub
            logger.info(f"Text extraction not implemented for file: {file_path}")
            return f"File content: {file_path}"

        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {e}")
            return None


text_extraction_service = TextExtractionService()
