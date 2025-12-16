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
    ApiUserCreate,
    ApiUserRead,
    ApiUserUpdate,
    Role as _UserRole,
)

UserRole = _UserRole  # Match the type of UserItem.role


class UserItem(ApiUserRead):
    """Represents a specific MindBridge User.

    ```py
    import mindbridgeapi as mbapi

    user = mbapi.UserItem(email="person@example.com", role=mbapi.UserRole.ROLE_USER)
    ```

    Attributes:
        id (str): The unique object identifier.
        email (str): The user's email address.
        enabled (bool): Indicates whether or not the user is enabled within this tenant.
        first_name (str): The user's first name.
        last_name (str): The user's last name.
        role (UserRole): The MindBridge role assigned to the user. [Learn about user roles](https://support.mindbridge.ai/hc/en-us/articles/360056394954-User-roles-available-in-MindBridge)
    """

    model_config = ConfigDict(
        extra="allow",
        validate_assignment=True,
        validate_default=True,
        validate_return=True,
    )
    _ = model_validator(mode="after")(_warning_if_extra_fields)

    def _get_post_json(
        self, out_class: type[ApiUserCreate | ApiUserUpdate]
    ) -> dict[str, Any]:
        in_class_dict = self.model_dump()
        out_class_object = out_class.model_validate(in_class_dict)
        return out_class_object.model_dump(
            mode="json", by_alias=True, exclude_none=True
        )

    @property
    def create_json(self) -> dict[str, Any]:
        return self._get_post_json(out_class=ApiUserCreate)

    @property
    def update_json(self) -> dict[str, Any]:
        return self._get_post_json(out_class=ApiUserUpdate)
