from typing import Optional

from galtea.utils.from_camel_case_base_model import FromCamelCaseBaseModel


class CostInfoProperties(FromCamelCaseBaseModel):
    cost_per_input_token: Optional[float] = None
    cost_per_output_token: Optional[float] = None
    cost_per_cache_read_input_token: Optional[float] = None
    cost: Optional[float] = None


class UsageInfoProperties(FromCamelCaseBaseModel):
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    cache_read_input_tokens: Optional[int] = None
    tokens: Optional[int] = None


# Legacy evaluation-based models (maintained for backward compatibility)
class InferenceResultBase(CostInfoProperties, UsageInfoProperties):
    """Model for creating inference results with mandatory fields (POST operation)."""

    session_id: str
    actual_input: Optional[str] = None
    actual_output: Optional[str] = None
    retrieval_context: Optional[str] = None
    latency: Optional[float] = None
    conversation_simulator_version: Optional[str] = None


class InferenceResult(InferenceResultBase):
    id: str
    index: int


class InferenceResultUpdate(FromCamelCaseBaseModel):
    """Model for updating inference results with all optional fields (PATCH operation).

    Fields are Optional (defaulting to None) so they can be excluded from serialization
    if not set (via exclude_unset=True in the service).
    """

    # Overridden from CostInfoProperties
    cost_per_input_token: Optional[float] = None
    cost_per_output_token: Optional[float] = None
    cost_per_cache_read_input_token: Optional[float] = None
    cost: Optional[float] = None

    # Overridden from UsageInfoProperties
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    cache_read_input_tokens: Optional[int] = None
    tokens: Optional[int] = None

    # Fields specific to InferenceResultUpdate
    session_id: Optional[str] = None
    actual_input: Optional[str] = None
    actual_output: Optional[str] = None
    retrieval_context: Optional[str] = None
    latency: Optional[float] = None
    conversation_simulator_version: Optional[str] = None
    index: Optional[int] = None
    created_at: Optional[str] = None
    deleted_at: Optional[str] = None
