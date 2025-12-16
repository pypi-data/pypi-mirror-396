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
    ApiEngagementAccountGroupCreate,
    ApiEngagementAccountGroupRead,
    ApiEngagementAccountGroupUpdate,
)


class EngagementAccountGroupItem(ApiEngagementAccountGroupRead):
    """Represents a specific MindBridge Engagement Account Group.

    ```py
    import mindbridgeapi as mbapi

    engagement_account_group_item = mbapi.EngagementAccountGroupItem(
        code="My New Code",
        description={"en": "My description"},
        hidden=False,
        parent_code="Parent Code",
        engagement_account_grouping_id="An actual engagement_account_grouping_id",
        mac_code="1101",
    )
    ```

    Attributes:
        id (str): The unique object identifier.
        alias (str): A replacement value used when displaying the account description.
            This does not have any effect on automatic column mapping.
        code (str): The account code for this account group.
        description (dict[str, str]]): A description of the account code for this
            account group.
        engagement_account_grouping_id (str): The unique identifier for the engagement
            account grouping that the engagement account group belongs to.
        hidden (bool): When `true` this account is hidden, and can't be used in account
            mapping. Additionally this account won't be suggested when automatically
            mapping accounts during file import.
        mac_code (str): The MAC code mapped to this account group.
        parent_code (str): The parent code for this account group.
    """

    model_config = ConfigDict(
        extra="allow",
        validate_assignment=True,
        validate_default=True,
        validate_return=True,
    )
    _ = model_validator(mode="after")(_warning_if_extra_fields)

    def _get_post_json(
        self,
        out_class: type[
            ApiEngagementAccountGroupCreate | ApiEngagementAccountGroupUpdate
        ],
    ) -> dict[str, Any]:
        in_class_dict = self.model_dump()
        out_class_object = out_class.model_validate(in_class_dict)
        return out_class_object.model_dump(
            mode="json", by_alias=True, exclude_none=True
        )

    @property
    def create_json(self) -> dict[str, Any]:
        return self._get_post_json(out_class=ApiEngagementAccountGroupCreate)

    @property
    def update_json(self) -> dict[str, Any]:
        return self._get_post_json(out_class=ApiEngagementAccountGroupUpdate)
