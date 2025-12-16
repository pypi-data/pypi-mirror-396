#
#  Copyright MindBridge Analytics Inc. all rights reserved.
#
#  This material is confidential and may not be copied, distributed,
#  reversed engineered, decompiled or otherwise disseminated without
#  the prior written consent of MindBridge Analytics Inc.
#

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any
from mindbridgeapi.base_set import BaseSet
from mindbridgeapi.common_validators import _convert_json_query
from mindbridgeapi.engagement_account_group_item import EngagementAccountGroupItem
from mindbridgeapi.exceptions import ItemAlreadyExistsError, ItemNotFoundError

if TYPE_CHECKING:
    from collections.abc import Generator


@dataclass
class EngagementAccountGroups(BaseSet):
    """Use to interact with Engagement Account Groups.

    Typical usage of these functions would be accessed from the server, for example:
    ```py
    import os
    import mindbridgeapi as mbapi

    server = mbapi.Server(
        url=os.environ["MINDBRIDGE_API_TEST_URL"],
        token=os.environ["MINDBRIDGE_API_TEST_TOKEN"],
    )

    engagement = server.engagements.get_by_id("An engagement id here...")
    engagement_account_grouping = next(engagement.engagement_account_groupings)

    engagement_account_group_item = mbapi.EngagementAccountGroupItem(
        code="abc",
        description={"en": "My description"},
        hidden=False,
        parent_code=next(
            x.code for x in engagement_account_grouping.engagement_account_groups
        ),
        engagement_account_grouping_id=engagement_account_grouping.id,
        mac_code="1101",
    )
    engagement_account_group_item = server.engagement_account_groups.create(
        engagement_account_group_item
    )
    print(f"Created {engagement_account_group_item.code}")
    ```
    """

    base_url: str = field(init=False)

    def __post_init__(self) -> None:
        self.base_url = f"{self.server.base_url}/engagement-account-groups"

    def create(
        self, engagement_account_group_item: EngagementAccountGroupItem
    ) -> EngagementAccountGroupItem:
        """Creates a new Engagement Account Group on the server.

        Args:
            engagement_account_group_item (EngagementAccountGroupItem): The Engagement
                Account Group to create.

        Returns:
            (EngagementAccountGroupItem): The created Engagement Account Group.

        Raises:
            ItemAlreadyExistsError: If the engagement_account_group_item already has an
                ID.
        """
        engagement_account_group_item = EngagementAccountGroupItem.model_validate(
            engagement_account_group_item
        )
        if engagement_account_group_item.id:
            raise ItemAlreadyExistsError(engagement_account_group_item.id)

        resp_dict = super()._create(
            url=self.base_url, json=engagement_account_group_item.create_json
        )
        return EngagementAccountGroupItem.model_validate(resp_dict)

    def delete(self, engagement_account_group_item: EngagementAccountGroupItem) -> None:
        """Deletes an existing Engagement Account Group.

        Args:
            engagement_account_group_item (EngagementAccountGroupItem): The Engagement
                Account Group to delete.

        Raises:
            ItemNotFoundError: If the engagement_account_group_item does not have an ID.
        """
        engagement_account_group_item = EngagementAccountGroupItem.model_validate(
            engagement_account_group_item
        )

        if not engagement_account_group_item.id:
            raise ItemNotFoundError

        super()._delete(url=f"{self.base_url}/{engagement_account_group_item.id}")

    def get(
        self, json: dict[str, Any] | None = None
    ) -> "Generator[EngagementAccountGroupItem, None, None]":
        """Retrieves Engagement Account Groups.

        Retrieves Engagement Account Groups rom the server based on the optionally
            provided query parameters.

        Args:
            json (dict[str, Any]): The query parameters.

        Yields:
            (EngagementAccountGroupItem): The next Engagement Account Group.
        """
        mb_query_dict = _convert_json_query(
            json, required_key="engagementAccountGroupingId"
        )

        for resp_dict in super()._get(url=f"{self.base_url}/query", json=mb_query_dict):
            yield EngagementAccountGroupItem.model_validate(resp_dict)

    def get_by_id(self, id: str) -> EngagementAccountGroupItem:
        """Retrieves an Engagement Account Group item by its ID.

        Args:
            id (str): The ID of the Engagement Account Group to retrieve.

        Returns:
            (EngagementAccountGroupItem): The retrieved Engagement Account Group.
        """
        resp_dict = super()._get_by_id(url=f"{self.base_url}/{id}")
        return EngagementAccountGroupItem.model_validate(resp_dict)

    def update(
        self, engagement_account_group_item: EngagementAccountGroupItem
    ) -> EngagementAccountGroupItem:
        """Updates an existing Engagement Account Group.

        Args:
            engagement_account_group_item (EngagementAccountGroupItem): The
                Engagement Account Group to update.

        Returns:
            (EngagementAccountGroupItem): The updated Engagement Account Group.

        Raises:
            ItemNotFoundError: If the engagement_account_group_item does not have an ID.
        """
        engagement_account_group_item = EngagementAccountGroupItem.model_validate(
            engagement_account_group_item
        )

        if not engagement_account_group_item.id:
            raise ItemNotFoundError

        resp_dict = super()._update(
            url=f"{self.base_url}/{engagement_account_group_item.id}",
            json=engagement_account_group_item.update_json,
        )

        return EngagementAccountGroupItem.model_validate(resp_dict)
