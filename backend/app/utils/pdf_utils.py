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

logger = logging.getLogger(__name__)

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