import json
import logging

from app.providers.llm.base_llm import BaseLLMProvider
from app.core.config import settings

logger = logging.getLogger(__name__)


class GeminiProvider(BaseLLMProvider):
    """
    Gemini LLM provider using the Google GenAI SDK.

    Uses batch evaluation:
    - One Gemini API call for the complete question paper.
    - Evaluates each question according to its Scheme of Evaluation.
    - Returns structured JSON.
    """

    MODEL_NAME = "gemini-3.5-flash-lite"

    def __init__(self):
        self.client = None

        try:
            from google import genai

            api_key = settings.gemini_api_key

            if not api_key:
                raise ValueError("Gemini API key is missing")

            self.client = genai.Client(
                api_key=api_key
            )

            logger.info(
                f"Gemini provider initialized successfully "
                f"using {self.MODEL_NAME}"
            )

        except Exception as e:
            logger.exception(
                f"Gemini initialization failed: {e}"
            )
            self.client = None

    def evaluate(
        self,
        question: str,
        model_answer: str,
        student_answer: str,
        criteria: list
    ) -> dict:
        """
        Evaluate a single question.

        Kept for compatibility with the BaseLLMProvider interface.
        Internally uses batch evaluation.
        """

        result = self.evaluate_batch([
            {
                "q_no": 1,
                "question": question,
                "model_answer": model_answer,
                "student_answer": student_answer,
                "criteria": criteria
            }
        ])

        if result and "questions" in result:
            questions = result["questions"]

            if questions:
                q = questions[0]

                return {
                    "scores": q.get("scores", []),
                    "total": q.get("total", 0),
                    "feedback": q.get("feedback", "")
                }

        return {
            "scores": [],
            "total": 0,
            "feedback": "Evaluation failed"
        }

    def evaluate_batch(self, questions: list) -> dict:
        """
        Evaluate ALL questions in ONE Gemini API call.

        Expected input:

        [
            {
                "q_no": 1,
                "question": "What is Java?",
                "model_answer": "...",
                "student_answer": "...",
                "criteria": [
                    {
                        "criterion": "Definition",
                        "marks": 2
                    },
                    {
                        "criterion": "Features",
                        "marks": 3
                    }
                ]
            }
        ]

        Returns:

        {
            "questions": [
                {
                    "question_no": 1,
                    "scores": [
                        {
                            "criterion": "Definition",
                            "awarded": 2,
                            "max": 2,
                            "reason": "Correct definition"
                        }
                    ],
                    "total": 5,
                    "feedback": "Good answer"
                }
            ]
        }
        """

        # ---------------------------------------------------------
        # 1. Check Gemini client
        # ---------------------------------------------------------

        if not self.client:
            raise RuntimeError(
                "Gemini client not initialized"
            )

        if not questions:
            logger.warning(
                "evaluate_batch called with no questions"
            )

            return {
                "questions": []
            }

        # ---------------------------------------------------------
        # 2. Build question prompts
        # ---------------------------------------------------------

        prompt_parts = []

        for q in questions:

            q_no = q.get("q_no")
            question = q.get("question", "")
            model_answer = q.get("model_answer", "")
            student_answer = q.get(
                "student_answer",
                "No answer provided"
            )
            criteria = q.get("criteria", [])

            scheme_lines = []

            for criterion in criteria:

                criterion_name = criterion.get(
                    "criterion",
                    ""
                )

                marks = criterion.get(
                    "marks",
                    0
                )

                scheme_lines.append(
                    f"    - {criterion_name}: {marks} marks"
                    + (
                        f"\n      Model answer: {criterion['model_answer']}"
                        if criterion.get("model_answer") else ""
                    )
                )

            scheme_text = "\n".join(
                scheme_lines
            )

            total_marks = sum(
                criterion.get("marks", 0)
                for criterion in criteria
            )

            prompt_parts.append(
                f"""
--- QUESTION {q_no} ---

Question:
{question}

Total Marks:
{total_marks}

Scheme of Evaluation:
{scheme_text}

Model Answer:
{model_answer}

Student Answer:
{student_answer}
"""
            )

        # ---------------------------------------------------------
        # 3. Build complete Gemini prompt
        # ---------------------------------------------------------

        full_prompt = f"""
You are a strict but fair VTU university examiner.

Your task is to evaluate the student's answers for ALL questions
provided below.

IMPORTANT EVALUATION RULES:

1. Evaluate every question independently.

2. Use the Scheme of Evaluation provided for each question.

3. Award marks criterion-by-criterion.

4. Do NOT award more marks than the maximum marks specified
   for a criterion.

5. The question total MUST equal the sum of the awarded marks
   for all criteria.

6. Award marks based on conceptual and semantic correctness,
   NOT exact word matching.

7. Minor spelling mistakes should NOT reduce marks if the
   technical meaning is clear.

8. Minor grammar mistakes should NOT reduce marks if the
   technical meaning is correct.

9. Student answers may come from OCR of handwritten answers.
   OCR may contain:
   - spelling errors
   - missing characters
   - incorrect words
   - broken sentences
   - unusual formatting

   Try to understand the student's intended meaning before
   deciding the marks.

10. Do NOT assume that an answer is correct merely because it
    contains keywords.

11. Do NOT award marks for concepts that are completely absent
    from the student's answer.

12. Compare the student's answer with the model answer, but
    evaluate according to the actual Scheme of Evaluation.

13. If the student gives a partially correct answer, award
    proportional marks.

14. If the student answer is completely wrong or irrelevant,
    award 0 where appropriate.

15. If the student has not answered a question, award 0 marks.

16. Feedback should briefly explain why marks were awarded or
    deducted.

17. Return ONLY valid JSON.

18. Do NOT return Markdown.

19. Do NOT wrap the JSON inside ```json or ``` blocks.

20. Do NOT add any text before or after the JSON.

QUESTIONS TO EVALUATE:

{chr(10).join(prompt_parts)}

Return EXACTLY this JSON structure:

{{
    "questions": [
        {{
            "question_no": 1,
            "scores": [
                {{
                    "criterion": "Criterion name",
                    "awarded": 4,
                    "max": 5,
                    "reason": "Brief explanation"
                }}
            ],
            "total": 4,
            "feedback": "Overall feedback for this question"
        }}
    ]
}}
"""

        # ---------------------------------------------------------
        # 4. Call Gemini
        # ---------------------------------------------------------

        try:

            logger.info(
                f"Sending {len(questions)} questions "
                f"to Gemini in one batch"
            )

            response = self.client.models.generate_content(
                model=self.MODEL_NAME,
                contents=full_prompt
            )

            # -----------------------------------------------------
            # 5. Get response text
            # -----------------------------------------------------

            if not response:
                raise ValueError(
                    "Gemini returned an empty response"
                )

            raw = response.text

            if not raw:
                raise ValueError(
                    "Gemini returned empty response text"
                )

            logger.debug(
                f"Gemini raw response length: {len(raw)}"
            )

            # -----------------------------------------------------
            # 6. Clean possible Markdown code fences
            # -----------------------------------------------------

            clean = raw.strip()

            if clean.startswith("```json"):
                clean = clean[
                    len("```json"):
                ]

            elif clean.startswith("```"):
                clean = clean[
                    len("```"):
                ]

            if clean.endswith("```"):
                clean = clean[:-3]

            clean = clean.strip()

            # -----------------------------------------------------
            # 7. Parse JSON
            # -----------------------------------------------------

            try:

                result = json.loads(clean)

            except json.JSONDecodeError as e:

                logger.error(
                    f"Gemini returned invalid JSON: {e}"
                )

                logger.error(
                    f"Raw Gemini response: {raw[:2000]}"
                )

                raise ValueError(
                    f"AI returned invalid JSON: {e}"
                )

            # -----------------------------------------------------
            # 8. Validate basic response structure
            # -----------------------------------------------------

            if not isinstance(result, dict):

                raise ValueError(
                    "Gemini response is not a JSON object"
                )

            if "questions" not in result:

                raise ValueError(
                    "Gemini response does not contain "
                    "'questions'"
                )

            if not isinstance(
                result["questions"],
                list
            ):

                raise ValueError(
                    "'questions' must be a list"
                )

            # -----------------------------------------------------
            # 9. Validate and normalize scores
            # -----------------------------------------------------

            # -----------------------------------------------------


            total_marks = 0

            for q_result in result["questions"]:

                q_total = 0

                for score in q_result.get("scores", []):

                    awarded = score.get("awarded", 0)
                    max_marks = score.get("max", 0)

                    # Convert to float safely
                    try:
                        awarded = float(awarded)
                    except (TypeError, ValueError):
                        awarded = 0.0

                    try:
                        max_marks = float(max_marks)
                    except (TypeError, ValueError):
                        max_marks = 0.0

                    # Never allow negative marks
                    awarded = max(0.0, awarded)

                    # Never allow awarded marks above maximum
                    awarded = min(awarded, max_marks)

                    # Convert whole-number floats to integers
                    if awarded.is_integer():
                        awarded = int(awarded)

                    if max_marks.is_integer():
                        max_marks = int(max_marks)

                    score["awarded"] = awarded
                    score["max"] = max_marks

                    q_total += awarded

                # Convert total to integer if it's a whole number
                if isinstance(q_total, float) and q_total.is_integer():
                    q_total = int(q_total)

                q_result["total"] = q_total

                total_marks += q_total

            # -----------------------------------------------------
            # 10. Log result
            # -----------------------------------------------------

            logger.info(
                f"Gemini batch evaluated "
                f"{len(questions)} questions — "
                f"total awarded: {total_marks}"
            )

            return result

        # ---------------------------------------------------------
        # 11. Handle API errors
        # ---------------------------------------------------------

        except ValueError:
            raise

        except Exception as e:

            logger.exception(
                f"Gemini batch evaluation failed: {e}"
            )

            raise