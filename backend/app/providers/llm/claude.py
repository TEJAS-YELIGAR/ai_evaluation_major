import json
import logging
from app.providers.llm.base_llm import BaseLLMProvider
from app.core.config import settings

logger = logging.getLogger(__name__)

class ClaudeProvider(BaseLLMProvider):
    """
    LLM evaluation provider using Anthropic Claude API.
    Evaluates student answers semantically — meaning not keywords.
    """

    def __init__(self):
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=settings.claude_api_key)
            logger.info("Claude provider initialized successfully")
        except Exception as e:
            logger.error(f"Claude initialization failed: {e}")
            self.client = None

    def evaluate(
        self,
        question: str,
        model_answer: str,
        student_answer: str,
        criteria: list
    ) -> dict:
        """
        Send everything to Claude and get back structured marks.
        Claude evaluates based on MEANING not exact word match.
        """
        if not self.client:
            raise RuntimeError("Claude client not initialized")

        total_marks = sum(c['marks'] for c in criteria)
        scheme_text = "\n".join([
            f"- {c['criterion']}: {c['marks']} marks"
            for c in criteria
        ])

        prompt = f"""You are a strict but fair VTU university examiner.
Evaluate the student answer based ONLY on the scheme of evaluation provided.
Award marks based on MEANING and CONCEPT — not exact word matching.
Return ONLY raw JSON — no markdown, no code fences, no explanation outside JSON.

QUESTION: {question}

SCHEME OF EVALUATION (Total: {total_marks} marks):
{scheme_text}

MODEL ANSWER: {model_answer}

STUDENT ANSWER: {student_answer}

Return this exact JSON structure:
{{
    "scores": [
        {{
            "criterion": "criterion name here",
            "awarded": 4,
            "max": 5,
            "reason": "explanation of marks given"
        }}
    ],
    "total": 7,
    "feedback": "overall feedback for the student"
}}"""

        try:
            response = self.client.messages.create(
                model="claude-haiku-20240307",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )

            raw = response.content[0].text
            # Clean up in case Claude adds markdown
            clean = raw.replace("```json", "").replace("```", "").strip()
            result = json.loads(clean)

            logger.info(f"Claude evaluated — total: {result.get('total')}/{total_marks}")
            return result

        except json.JSONDecodeError as e:
            logger.error(f"Claude returned invalid JSON: {e}")
            raise ValueError(f"AI returned invalid response: {e}")
        except Exception as e:
            logger.error(f"Claude evaluation failed: {e}")
            raise