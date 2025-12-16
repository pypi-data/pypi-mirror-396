#
#  Copyright MindBridge Analytics Inc. all rights reserved.
#
#  This material is confidential and may not be copied, distributed,
#  reversed engineered, decompiled or otherwise disseminated without
#  the prior written consent of MindBridge Analytics Inc.
#

from typing import Any
from pydantic import ConfigDict, field_validator, model_validator
from mindbridgeapi.common_validators import (
    _convert_userinfo_to_useritem,
    _warning_if_extra_fields,
)
from mindbridgeapi.generated_pydantic_model.model import (
    ApiAccountMappingRead,
    ApiAccountMappingUpdate,
)


class AccountMappingItem(ApiAccountMappingRead):
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
        out_class_object = ApiAccountMappingUpdate.model_validate(in_class_dict)
        return out_class_object.model_dump(
            mode="json", by_alias=True, exclude_none=True
        )
