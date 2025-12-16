"""
Custom metric utilities for defining and executing custom evaluation metrics.
"""

from abc import ABC, abstractmethod
from typing import Optional


class CustomScoreEvaluationMetric(ABC):
    """
    Abstract base class for custom evaluation metrics.

    This class provides an interface for creating custom metrics that can be
    used with user-defined scoring functions.

    When initializing, you must provide either 'name' or 'id' to identify the metric,
    but not both. This identifier will be used when sending evaluation data to the API.

    Subclasses must implement the measure method, which should return a float score between 0.0 and 1.0.

    Example:
        >>> class MyCustomMetric(CustomScoreEvaluationMetric):
        ...     def measure(self, input, actual_output, expected_output, retrieval_context, context):
        ...         # Your custom scoring logic
        ...         return 0.85
        >>>
        >>> # Initialize with name
        >>> metric_by_name = MyCustomMetric(name="my_metric")
        >>>
        >>> # OR initialize with id
        >>> metric_by_id = MyCustomMetric(id="metric_123")
    """

    def __init__(self, name: Optional[str] = None, id: Optional[str] = None) -> None:
        """
        Initialize a custom evaluation metric.

        Args:
            name (Optional[str]): The name of the metric. Either name or id must be provided, but not both.
            id (Optional[str]): The ID of the metric. Either name or id must be provided, but not both.

        Raises:
            ValueError: If both name and id are provided, or if neither is provided.
        """
        if name is not None and id is not None:
            raise ValueError("Provide either 'name' or 'id', not both.")
        if name is None and id is None:
            raise ValueError("Either 'name' or 'id' must be provided.")

        self.name: Optional[str] = name
        self.id: Optional[str] = id

    @abstractmethod
    def measure(
        self,
        input: Optional[str] = None,
        actual_output: Optional[str] = None,
        expected_output: Optional[str] = None,
        retrieval_context: Optional[str] = None,
        context: Optional[str] = None,
    ) -> float:
        """
        Compute the score for the given actual output.

        Args:
            input (Optional[str]): The user query sent to the AI system.
            actual_output (Optional[str]): The actual output from the AI system.
            expected_output (Optional[str]): The expected output from the AI system.
            retrieval_context (Optional[str]): Context retrieved from the system.
            context (Optional[str]): Additional context for the evaluation.

        Returns:
            float: Score between 0.0 and 1.0.

        Raises:
            ValueError: If the score is not between 0.0 and 1.0.
        """
        pass

    def validate_score(self, score: float) -> float:
        """
        Validate that the score is within the expected range [0.0, 1.0].

        Args:
            score (float): The score to validate.

        Returns:
            float: The validated score.

        Raises:
            ValueError: If the score is not between 0.0 and 1.0.
        """
        if not isinstance(score, (int, float)):
            raise ValueError(f"Score must be a number, got {type(score)}")

        if not (0.0 <= score <= 1.0):
            raise ValueError(f"Score must be between 0.0 and 1.0, got {score}")

        return float(score)

    def __call__(
        self,
        input: Optional[str] = None,
        actual_output: Optional[str] = None,
        expected_output: Optional[str] = None,
        retrieval_context: Optional[str] = None,
        context: Optional[str] = None,
    ) -> float:
        """
        Make the metric callable, returning a validated score.

        Args:
            input (Optional[str]): The user query sent to the AI system.
            actual_output (Optional[str]): The actual output from the AI system.
            expected_output (Optional[str]): The expected output from the AI system.
            retrieval_context (Optional[str]): Context retrieved from the system.
            context (Optional[str]): Additional context for the evaluation.

        Returns:
            float: The validated score.
        """
        score: float = self.measure(
            input=input,
            actual_output=actual_output,
            expected_output=expected_output,
            retrieval_context=retrieval_context,
            context=context,
        )
        return self.validate_score(score)
