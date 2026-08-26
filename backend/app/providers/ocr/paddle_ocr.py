import logging
import numpy as np
from app.providers.ocr.base_ocr import BaseOCRProvider

logger = logging.getLogger(__name__)

class PaddleOCRProvider(BaseOCRProvider):
    """
    OCR provider using PaddleOCR.
    Completely FREE — runs locally inside Docker.
    No internet or API key needed.
    Good for handwritten and printed text.
    """

    def __init__(self):
        try:
            from paddleocr import PaddleOCR
            # use_angle_cls=True handles rotated/tilted text
            # lang='en' for English handwriting
            self.ocr = PaddleOCR(
                use_angle_cls=True,
                lang='en',
                show_log=False
            )
            logger.info("PaddleOCR initialized successfully")
        except Exception as e:
            logger.error(f"PaddleOCR initialization failed: {e}")
            self.ocr = None

    def extract_text(self, image_bytes: bytes) -> str:
        """
        Extract text from image bytes using PaddleOCR.
        Works for both printed and handwritten text.
        """
        if not self.ocr:
            logger.error("PaddleOCR not initialized")
            return ""

        try:
            # Convert bytes to numpy array
            import cv2
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if img is None:
                logger.error("Could not decode image")
                return ""

            # Run OCR
            result = self.ocr.ocr(img, cls=True)

            if not result or not result[0]:
                logger.warning("PaddleOCR returned no text")
                return ""

            # Extract text from result
            # Result format: [[[box], (text, confidence)], ...]
            lines = []
            for line in result[0]:
                if line and len(line) >= 2:
                    text = line[1][0]        # extracted text
                    confidence = line[1][1]  # confidence score

                    # Only include text with >50% confidence
                    if confidence > 0.5:
                        lines.append(text)

            full_text = " ".join(lines)
            logger.info(f"PaddleOCR extracted {len(full_text)} chars")
            return full_text

        except Exception as e:
            logger.error(f"PaddleOCR extraction failed: {e}")
            return ""