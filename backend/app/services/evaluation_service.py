import logging
from app.providers.llm.gemini import GeminiProvider
from app.providers.ocr.paddle_ocr import PaddleOCRProvider
from app.utils.pdf_utils import pdf_to_text_direct, pdf_to_images
from app.utils.text_utils import split_by_question
from app.repositories import soe_repo, evaluation_repo, booklet_repo

logger = logging.getLogger(__name__)

llm_provider = GeminiProvider()
ocr_provider = PaddleOCRProvider()


def run(booklet_id: int, db):
    """
    Full evaluation pipeline for one booklet.
    Evaluates and saves one question at a time so progress is visible.
    """
    logger.info(f"Starting evaluation for booklet {booklet_id}")
    booklet_repo.set_status(db, booklet_id, "processing")

    try:
        # Step 1: Get booklet and SoE
        booklet = booklet_repo.get(db, booklet_id)
        if not booklet:
            raise ValueError(f"Booklet {booklet_id} not found")

        soe_items = soe_repo.get_by_subject(db, booklet.subject_id)
        if not soe_items:
            raise ValueError(f"No SoE for subject {booklet.subject_id}")

        logger.info(f"SoE has {len(soe_items)} criteria")

        # Step 2: Extract text from PDF
        full_text = pdf_to_text_direct(booklet.pdf_path)

        if len(full_text.strip()) >= 20:
            logger.info(f"Typed PDF — direct text: {len(full_text)} chars")
            answers = split_by_question(full_text)
        else:
            # Handwritten PDF — use PaddleOCR page by page
            logger.info("Handwritten PDF — using PaddleOCR")
            images = pdf_to_images(booklet.pdf_path)
            page_texts = []

            for i, img_bytes in enumerate(images):
                page_text = ocr_provider.extract_text(img_bytes)
                logger.info(f"Page {i+1}: {len(page_text)} chars")
                if page_text.strip():
                    page_texts.append(page_text)

            if len(page_texts) > 1:
                # Multiple pages → each page = one question
                logger.info(f"Page-based split: {len(page_texts)} pages")
                answers = {i + 1: text for i, text in enumerate(page_texts)}
            else:
                # Single page → try marker split
                full_text = page_texts[0] if page_texts else ""
                answers = split_by_question(full_text)
                if not answers and full_text.strip():
                    answers = {1: full_text}

        logger.info(f"Answers found: {list(answers.keys())}")

        # Step 3: Build questions for sequential evaluation
        question_nos = sorted(set(s.question_no for s in soe_items))

        for q_no in question_nos:
            criteria = [
                {
                    "criterion": s.criterion_name,
                    "marks": s.max_marks,
                    "model_answer": s.model_answer
                }
                for s in soe_items if s.question_no == q_no
            ]
            model_answer = "\n\n".join(
                s.model_answer
                for s in soe_items
                if s.question_no == q_no and s.model_answer
            )
            student_answer = answers.get(q_no, "No answer provided")

            logger.info(f"Q{q_no} answer preview: {student_answer[:80]}")

            logger.info(f"Evaluating Q{q_no}")
            result = llm_provider.evaluate(
                question=f"Question {q_no}",
                model_answer=model_answer,
                student_answer=student_answer,
                criteria=criteria
            )
            evaluation_repo.save(db, booklet_id, q_no, result)
            logger.info(f"Q{q_no}: {result.get('total', 0)} marks saved")

        booklet_repo.set_status(db, booklet_id, "completed")
        logger.info(f"Booklet {booklet_id} COMPLETED ✅")

    except Exception as e:
        logger.error(f"Booklet {booklet_id} FAILED: {e}")
        booklet_repo.set_status(db, booklet_id, "failed")
        raise