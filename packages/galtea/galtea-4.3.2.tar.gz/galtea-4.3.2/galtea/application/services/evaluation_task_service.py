from typing import Dict, List, Optional, Union

from galtea.application.services.evaluation_service import EvaluationService
from galtea.application.services.metric_type_service import MetricTypeService
from galtea.application.services.session_service import SessionService
from galtea.application.services.test_case_service import TestCaseService
from galtea.domain.models.evaluation_task import EvaluationTask
from galtea.infrastructure.clients.http_client import Client
from galtea.utils.custom_score_metric import CustomScoreEvaluationMetric


class EvaluationTaskService:
    """
    Service for managing Evaluation Tasks.
    An Evaluation Task is the result of an evaluation against a specific metric and its criteria.
    Evaluations are created implicitly when evaluation tasks are created.
    """

    def __init__(
        self,
        client: Client,
        evaluation_service: EvaluationService,
        metric_type_service: MetricTypeService,
        session_service: SessionService,
        test_case_service: TestCaseService,
    ):
        self.__client = client
        self.__evaluation_service = evaluation_service
        self.__metric_type_service = metric_type_service
        self.__session_service = session_service
        self.__test_case_service = test_case_service

    def create_single_turn(
        self,
        version_id: str,
        actual_output: str,
        metrics: Optional[List[Union[str, CustomScoreEvaluationMetric]]] = None,
        metric_ids: Optional[List[str]] = None,
        test_case_id: Optional[str] = None,
        input: Optional[str] = None,
        is_production: Optional[bool] = None,
        retrieval_context: Optional[str] = None,
        latency: Optional[float] = None,
        usage_info: Optional[Dict[str, float]] = None,
        cost_info: Optional[Dict[str, float]] = None,
        conversation_simulator_version: Optional[str] = None,
    ) -> Optional[List[EvaluationTask]]:
        """
        Deprecated: The concept of "EvaluationTask" has been renamed to "Evaluation". Use "galtea.evaluations.create_single_turn" instead.
        """
        raise NotImplementedError(
            "The concept of 'EvaluationTask' has been renamed to 'Evaluation'. "
            "Use 'galtea.evaluations.create_single_turn' instead."
        )

    def create(
        self,
        metrics: List[str],
        session_id: str,
    ) -> List[EvaluationTask]:
        """
        Deprecated: The concept of "EvaluationTask" has been renamed to "Evaluation". Use "galtea.evaluations.create" instead.
        """
        raise NotImplementedError(
            "The concept of 'EvaluationTask' has been renamed to 'Evaluation'. Use 'galtea.evaluations.create' instead."
        )

    def get(self, evaluation_task_id: str):
        """
        Deprecated: The concept of "EvaluationTask" has been renamed to "Evaluation".
        Use "galtea.evaluations.get" instead.
        """
        raise NotImplementedError(
            "The concept of 'EvaluationTask' has been renamed to 'Evaluation'. Use 'galtea.evaluations.get' instead."
        )

    def list(
        self,
        session_id: Optional[str] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ):
        """
        Deprecated: The concept of "EvaluationTask" has been renamed to "Evaluation".
        Use "galtea.evaluations.list" instead.
        """
        raise NotImplementedError(
            "The concept of 'EvaluationTask' has been renamed to 'Evaluation'. Use 'galtea.evaluations.list' instead."
        )

    def delete(self, evaluation_task_id: str):
        """
        Deprecated: The concept of "EvaluationTask" has been renamed to "Evaluation".
        Use "galtea.evaluations.delete" instead.
        """
        raise NotImplementedError(
            "The concept of 'EvaluationTask' has been renamed to 'Evaluation'. Use 'galtea.evaluations.delete' instead."
        )
