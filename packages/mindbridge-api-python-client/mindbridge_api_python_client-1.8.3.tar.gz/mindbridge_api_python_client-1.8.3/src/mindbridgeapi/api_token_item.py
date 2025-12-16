#
#  Copyright MindBridge Analytics Inc. all rights reserved.
#
#  This material is confidential and may not be copied, distributed,
#  reversed engineered, decompiled or otherwise disseminated without
#  the prior written consent of MindBridge Analytics Inc.
#

from typing import Annotated, Any
from pydantic import ConfigDict, Field, field_validator, model_validator
from mindbridgeapi.common_validators import (
    _convert_userinfo_to_useritem,
    _warning_if_extra_fields,
)
from mindbridgeapi.generated_pydantic_model.model import (
    ApiApiTokenCreate,
    ApiApiTokenRead,
    ApiApiTokenUpdate,
    CreateApiTokenResponseRead,
    Permission as _ApiTokenPermission,
)

ApiTokenPermission = (
    _ApiTokenPermission  # Match the type of the list items of ApiTokenItem.permissions
)


class ApiTokenItem(ApiApiTokenRead):
    """Represents a specific MindBridge API token.

    ```py
    from datetime import datetime, timedelta, timezone
    import mindbridgeapi as mbapi

    token = mbapi.ApiTokenItem(
        name="My Token Name",
        expiry=datetime.now(tz=timezone.utc) + timedelta(hours=1),
        permissions=[mbapi.ApiTokenPermission.API_ORGANIZATIONS_READ],
    )
    ```

    Attributes:
        id (str): The unique object identifier.
        name (str): The token record's name. This will also be used as the API Token
            User's name.
        expiry (datetime): When the API token expires. The value must have timezone
            info.
        permissions (list[ApiTokenPermission]): The set of permissions that inform which
            endpoints this token is authorized to access.
        allowed_addresses (Optional[list[str]]): Indicates the set of addresses that are
            allowed to use this token. If empty, any address may use it.
        partial_token (str): A partial representation of the API token.
        user_id (str): Identifies the API Token User associated with this token.
        token (str): The token string associated with the API token.
    """

    permissions: Annotated[
        list[ApiTokenPermission | str] | None,
        Field(description=ApiApiTokenRead.model_fields["permissions"].description),
    ] = None  # type: ignore[assignment]
    token: Annotated[
        str | None,
        Field(description=CreateApiTokenResponseRead.model_fields["token"].description),
    ] = None

    model_config = ConfigDict(
        extra="allow",
        validate_assignment=True,
        validate_default=True,
        validate_return=True,
    )
    _a = model_validator(mode="after")(_warning_if_extra_fields)
    _b = field_validator("*")(_convert_userinfo_to_useritem)

    def _get_post_json(
        self, out_class: type[ApiApiTokenCreate | ApiApiTokenUpdate]
    ) -> dict[str, Any]:
        in_class_dict = self.model_dump()
        out_class_object = out_class.model_validate(in_class_dict)
        return out_class_object.model_dump(
            mode="json", by_alias=True, exclude_none=True
        )

    @property
    def create_json(self) -> dict[str, Any]:
        return self._get_post_json(out_class=ApiApiTokenCreate)

    @property
    def update_json(self) -> dict[str, Any]:
        return self._get_post_json(out_class=ApiApiTokenUpdate)
