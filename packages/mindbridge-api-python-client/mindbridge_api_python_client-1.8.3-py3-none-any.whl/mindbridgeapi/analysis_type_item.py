#
#  Copyright MindBridge Analytics Inc. all rights reserved.
#
#  This material is confidential and may not be copied, distributed,
#  reversed engineered, decompiled or otherwise disseminated without
#  the prior written consent of MindBridge Analytics Inc.
#

from collections.abc import Generator
from typing import Annotated, ClassVar
from pydantic import ConfigDict, Field, field_validator, model_validator
from mindbridgeapi.analysis_source_type_item import AnalysisSourceTypeItem
from mindbridgeapi.common_validators import (
    _convert_userinfo_to_useritem,
    _warning_if_extra_fields,
)
from mindbridgeapi.generated_pydantic_model.model import ApiAnalysisTypeRead


def _empty_analysis_source_types() -> Generator[AnalysisSourceTypeItem, None, None]:
    """Empty generator function.

    This returns an empty generator function, it's use is to ensure
    analysis_source_types is not None for the AnalysisTypeItem class

    Yields:
        AnalysisSourceTypeItem: Will never yield anything
    """
    yield from ()


class AnalysisTypeItem(ApiAnalysisTypeRead):
    GENERAL_LEDGER: ClassVar[str] = "4b8360d00000000000000000"
    NOT_FOR_PROFIT_GENERAL_LEDGER: ClassVar[str] = "4b8360d00000000000000001"
    NOT_FOR_PROFIT_GENERAL_LEDGER_FUND: ClassVar[str] = "4b8360d00000000000000002"
    ACCOUNTS_PAYABLE_V2: ClassVar[str] = "4b8360d00000000000000003"
    ACCOUNTS_RECEIVABLE_V2: ClassVar[str] = "4b8360d00000000000000004"
    analysis_source_types: Annotated[
        Generator[AnalysisSourceTypeItem, None, None], Field(exclude=True)
    ] = _empty_analysis_source_types()

    model_config = ConfigDict(
        extra="allow",
        validate_assignment=True,
        validate_default=True,
        validate_return=True,
    )
    _a = model_validator(mode="after")(_warning_if_extra_fields)
    _b = field_validator("*")(_convert_userinfo_to_useritem)
