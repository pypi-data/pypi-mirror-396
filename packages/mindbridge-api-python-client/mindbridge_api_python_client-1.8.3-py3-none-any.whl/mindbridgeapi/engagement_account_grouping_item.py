#
#  Copyright MindBridge Analytics Inc. all rights reserved.
#
#  This material is confidential and may not be copied, distributed,
#  reversed engineered, decompiled or otherwise disseminated without
#  the prior written consent of MindBridge Analytics Inc.
#

from collections.abc import Generator
from typing import Annotated
from pydantic import ConfigDict, Field, field_validator, model_validator
from mindbridgeapi.common_validators import (
    _convert_userinfo_to_useritem,
    _warning_if_extra_fields,
)
from mindbridgeapi.engagement_account_group_item import EngagementAccountGroupItem
from mindbridgeapi.generated_pydantic_model.model import (
    ApiEngagementAccountGroupingRead,
)


def _empty_engagement_account_groups() -> Generator[
    EngagementAccountGroupItem, None, None
]:
    """Empty generator function.

    This returns an empty generator function, it's use is to ensure
    engagement_account_groups is not None for the EngagementAccountGroupingItem class

    Yields:
        EngagementAccountGroupItem: Will never yield anything
    """
    yield from ()


class EngagementAccountGroupingItem(ApiEngagementAccountGroupingRead):
    engagement_account_groups: Annotated[
        Generator[EngagementAccountGroupItem, None, None], Field(exclude=True)
    ] = _empty_engagement_account_groups()

    model_config = ConfigDict(
        extra="allow",
        validate_assignment=True,
        validate_default=True,
        validate_return=True,
    )
    _a = model_validator(mode="after")(_warning_if_extra_fields)
    _b = field_validator("*")(_convert_userinfo_to_useritem)
