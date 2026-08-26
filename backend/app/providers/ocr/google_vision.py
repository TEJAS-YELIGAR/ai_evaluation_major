import logging
from app.providers.ocr.base_ocr import BaseOCRProvider

logger = logging.getLogger(__name__)

class GoogleVisionOCR(BaseOCRProvider):
    """
    OCR provider using Google Cloud Vision API.
    Reads handwritten text from images.
    """

    def __init__(self):
        try:
            from google.cloud import vision
            self.client = vision.ImageAnnotatorClient()
            self.vision = vision
            logger.info("Google Vision OCR initialized successfully")
        except Exception as e:
            logger.warning(f"Google Vision not available: {e}")
            self.client = None

    def extract_text(self, image_bytes: bytes) -> str:
        """Send image to Google Vision, get back text."""
        if not self.client:
            logger.warning("Google Vision client not available, returning empty string")
            return ""

        try:
            image = self.vision.Image(content=image_bytes)
            response = self.client.document_text_detection(image=image)

            if response.error.message:
                logger.error(f"Google Vision error: {response.error.message}")
                return ""

            text = response.full_text_annotation.text
            logger.info(f"OCR extracted {len(text)} characters")
            return text

        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            return ""