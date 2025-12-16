#
#  Copyright MindBridge Analytics Inc. all rights reserved.
#
#  This material is confidential and may not be copied, distributed,
#  reversed engineered, decompiled or otherwise disseminated without
#  the prior written consent of MindBridge Analytics Inc.
#

from typing import Any
from pydantic import ConfigDict, model_validator
from mindbridgeapi.common_validators import _warning_if_extra_fields
from mindbridgeapi.generated_pydantic_model.model import (
    ApiAccountGroupRead,
    ApiAccountGroupUpdate,
)


class AccountGroupItem(ApiAccountGroupRead):
    model_config = ConfigDict(
        extra="allow",
        validate_assignment=True,
        validate_default=True,
        validate_return=True,
    )
    _ = model_validator(mode="after")(_warning_if_extra_fields)

    @property
    def update_json(self) -> dict[str, Any]:
        in_class_dict = self.model_dump()
        ag_update = ApiAccountGroupUpdate.model_validate(in_class_dict)
        return ag_update.model_dump(mode="json", by_alias=True, exclude_none=True)
