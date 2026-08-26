from abc import ABC, abstractmethod

class BaseLLMProvider(ABC):
    """
    Abstract base class for LLM evaluation providers.
    Any LLM tool must implement evaluate().
    """

    @abstractmethod
    def evaluate(
        self,
        question: str,
        model_answer: str,
        student_answer: str,
        criteria: list
    ) -> dict:
        """
        Evaluates student answer against model answer.

        criteria = [
            {"criterion": "Theory explanation", "marks": 5},
            {"criterion": "Diagram with labels", "marks": 5}
        ]

        Returns:
        {
            "scores": [
                {"criterion": "...", "awarded": 4, "max": 5, "reason": "..."}
            ],
            "total": 7,
            "feedback": "..."
        }
        """
        ...