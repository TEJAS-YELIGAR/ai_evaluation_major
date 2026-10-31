# import fitz  # PyMuPDF
# import logging

# logger = logging.getLogger(__name__)

# def pdf_to_images(pdf_path: str) -> list:
#     """
#     Convert each page of a PDF to image bytes.

#     Input:  path to PDF file
#     Output: list of bytes (one per page)
#     """
#     images = []
#     try:
#         pdf = fitz.open(pdf_path)
#         logger.info(f"PDF has {len(pdf)} pages")

#         for page_num in range(len(pdf)):
#             page = pdf[page_num]
#             # Render page at 2x zoom for better OCR quality
#             mat = fitz.Matrix(2, 2)
#             pix = page.get_pixmap(matrix=mat)
#             img_bytes = pix.tobytes("png")
#             images.append(img_bytes)
#             logger.info(f"Page {page_num + 1} converted to image")

#         pdf.close()
#     except Exception as e:
#         logger.error(f"PDF conversion failed: {e}")
#         raise

#     return images



import fitz  # PyMuPDF
import logging
from app.providers.ocr.paddle_ocr import get_paddle_ocr_provider
from app.utils.text_utils import has_unrecognized_glyphs

logger = logging.getLogger(__name__)


def prefer_ocr_text(direct_text: str, ocr_text: str) -> str:
    if (
        has_unrecognized_glyphs(direct_text)
        and ocr_text.strip()
        and not has_unrecognized_glyphs(ocr_text)
    ):
        return ocr_text.strip()
    return direct_text.strip()


def pdf_to_text_direct(pdf_path: str) -> str:
    """
    Extract text directly from text-based PDFs.
    No OCR needed — works for PDFs created from Word/Chrome.
    Much faster and more accurate than OCR for typed PDFs.
    """
    full_text = ""
    try:
        pdf = fitz.open(pdf_path)
        logger.info(f"PDF has {len(pdf)} pages")

        for page_num in range(len(pdf)):
            page = pdf[page_num]
            text = page.get_text()  # direct text extraction
            full_text += text + "\n"
            logger.info(f"Page {page_num + 1}: extracted {len(text)} chars")

        pdf.close()
        logger.info(f"Total text extracted: {len(full_text)} chars")
    except Exception as e:
        logger.error(f"PDF text extraction failed: {e}")
        raise

    return full_text


def pdf_to_text_with_ocr_fallback(pdf_path: str) -> str:
    """Extract PDF text directly and OCR only pages with missing glyphs."""
    page_texts = []
    ocr_provider = None

    try:
        with fitz.open(pdf_path) as pdf:
            logger.info(f"PDF has {len(pdf)} pages")
            for page_num, page in enumerate(pdf):
                direct_text = page.get_text()
                if has_unrecognized_glyphs(direct_text):
                    if ocr_provider is None:
                        ocr_provider = get_paddle_ocr_provider()
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                    ocr_text = ocr_provider.extract_text(pix.tobytes("png"))
                    page_text = prefer_ocr_text(direct_text, ocr_text)
                    if page_text == direct_text.strip():
                        logger.warning(
                            "OCR did not improve question-paper text on page %s",
                            page_num + 1,
                        )
                    else:
                        logger.info(
                            "Used OCR for question-paper page %s",
                            page_num + 1,
                        )
                else:
                    page_text = direct_text.strip()
                page_texts.append(page_text)
    except Exception:
        logger.exception("Question-paper text extraction failed")
        raise

    return "\n\n".join(text for text in page_texts if text)


def pdf_to_images(pdf_path: str) -> list:
    """
    Convert each page of a PDF to image bytes.
    Used for scanned/handwritten PDFs with Google Vision OCR.
    """
    images = []
    try:
        pdf = fitz.open(pdf_path)
        for page_num in range(len(pdf)):
            page = pdf[page_num]
            mat = fitz.Matrix(2, 2)
            pix = page.get_pixmap(matrix=mat)
            img_bytes = pix.tobytes("png")
            images.append(img_bytes)
        pdf.close()
    except Exception as e:
        logger.error(f"PDF to images failed: {e}")
        raise

    return images