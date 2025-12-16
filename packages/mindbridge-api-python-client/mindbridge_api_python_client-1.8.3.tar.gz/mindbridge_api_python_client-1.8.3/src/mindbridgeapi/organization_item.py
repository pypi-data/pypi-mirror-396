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
from mindbridgeapi.common_validators import (
    _convert_userinfo_to_useritem,
    _warning_if_extra_fields,
)
from mindbridgeapi.engagement_item import EngagementItem
from mindbridgeapi.generated_pydantic_model.model import (
    ApiOrganizationCreate,
    ApiOrganizationRead,
    ApiOrganizationUpdate,
)


def _empty_engagements() -> Generator[EngagementItem, None, None]:
    """Empty generator function.

    This returns an empty generator function, it's use is to ensure engagements is not
    None for the OrganizationItem class

    Yields:
        EngagementItem: Will never yield anything
    """
    yield from ()


class OrganizationItem(ApiOrganizationRead):
    """Represents a specific MindBridge Organization.

    ```py
    import mindbridgeapi as mbapi

    organization = mbapi.OrganizationItem(name="My Organization Name")
    ```

    Attributes:
        id (str): Unique identifier for items created on MindBridge
        name (str): The name of the organization
        external_client_code (Optional[str]): The unique client ID applied to this
            organization
        manager_user_ids (Optional[list[str]]): Identifies users assigned to the
            organization manager role
    """

    engagements: Annotated[
        Generator[EngagementItem, None, None], Field(exclude=True)
    ] = _empty_engagements()

    model_config = ConfigDict(
        extra="allow",
        validate_assignment=True,
        validate_default=True,
        validate_return=True,
    )
    _a = model_validator(mode="after")(_warning_if_extra_fields)
    _b = field_validator("*")(_convert_userinfo_to_useritem)

    def _get_post_json(
        self, out_class: type[ApiOrganizationCreate | ApiOrganizationUpdate]
    ) -> dict[str, Any]:
        in_class_dict = self.model_dump()
        out_class_object = out_class.model_validate(in_class_dict)
        return out_class_object.model_dump(
            mode="json", by_alias=True, exclude_none=True
        )

    @property
    def create_json(self) -> dict[str, Any]:
        return self._get_post_json(out_class=ApiOrganizationCreate)

    @property
    def update_json(self) -> dict[str, Any]:
        return self._get_post_json(out_class=ApiOrganizationUpdate)
