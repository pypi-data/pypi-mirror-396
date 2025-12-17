from typing import List, Optional

from galtea.utils.from_camel_case_base_model import FromCamelCaseBaseModel


class TestBase(FromCamelCaseBaseModel):
    product_id: Optional[str] = None
    name: str
    type: str
    language_code: Optional[str] = None
    ground_truth_uri: Optional[str] = None
    few_shot: Optional[str] = None
    custom_user_persona: Optional[str] = None
    variants: Optional[List[str]] = None
    strategies: Optional[List[str]] = None
    custom_user_persona: Optional[str] = None
    custom_variant_description: Optional[str] = None
    max_test_cases: Optional[int] = None
    uri: Optional[str] = None


class Test(TestBase):
    id: str
    created_at: str
    deleted_at: Optional[str] = None
