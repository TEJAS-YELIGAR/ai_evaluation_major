from abc import ABC, abstractmethod

class BaseOCRProvider(ABC):
    """
    Abstract base class for OCR providers.
    Any OCR tool must implement extract_text().
    """

    @abstractmethod
    def extract_text(self, image_bytes: bytes) -> str:
        """
        Takes image as bytes.
        Returns extracted text as string.
        """
        ...