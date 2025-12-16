#
#  Copyright MindBridge Analytics Inc. all rights reserved.
#
#  This material is confidential and may not be copied, distributed,
#  reversed engineered, decompiled or otherwise disseminated without
#  the prior written consent of MindBridge Analytics Inc.
#

from collections.abc import Generator
from typing import Annotated, Any
from pydantic import ConfigDict, Field, field_validator, model_validator
from mindbridgeapi.account_group_item import AccountGroupItem
from mindbridgeapi.common_validators import (
    _convert_userinfo_to_useritem,
    _warning_if_extra_fields,
)
from mindbridgeapi.generated_pydantic_model.model import (
    ApiAccountGroupingRead,
    ApiAccountGroupingUpdate,
    Type63 as _AccountGroupingFileType,
)

# Match the type of ApiImportAccountGroupingParamsCreate.type:
AccountGroupingFileType = _AccountGroupingFileType


def _empty_account_groups() -> Generator[AccountGroupItem, None, None]:
    """Empty generator function.

    This returns an empty generator function, it's use is to ensure account_groups is
    not None for the AccountGroupingItem class

    Yields:
        AccountGroupItem: Will never yield anything
    """
    yield from ()


class AccountGroupingItem(ApiAccountGroupingRead):
    account_groups: Annotated[
        Generator[AccountGroupItem, None, None], Field(exclude=True)
    ] = _empty_account_groups()

    model_config = ConfigDict(
        extra="allow",
        validate_assignment=True,
        validate_default=True,
        validate_return=True,
    )
    _a = model_validator(mode="after")(_warning_if_extra_fields)
    _b = field_validator("*")(_convert_userinfo_to_useritem)

    @property
    def update_json(self) -> dict[str, Any]:
        in_class_dict = self.model_dump()
        ag_update = ApiAccountGroupingUpdate.model_validate(in_class_dict)
        return ag_update.model_dump(mode="json", by_alias=True, exclude_none=True)
