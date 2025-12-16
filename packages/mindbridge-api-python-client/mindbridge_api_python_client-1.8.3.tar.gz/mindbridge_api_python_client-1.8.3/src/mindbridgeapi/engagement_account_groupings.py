#
#  Copyright MindBridge Analytics Inc. all rights reserved.
#
#  This material is confidential and may not be copied, distributed,
#  reversed engineered, decompiled or otherwise disseminated without
#  the prior written consent of MindBridge Analytics Inc.
#

from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING, Any
from mindbridgeapi.async_result_item import AsyncResultItem, AsyncResultType
from mindbridgeapi.base_set import BaseSet
from mindbridgeapi.engagement_account_grouping_item import EngagementAccountGroupingItem
from mindbridgeapi.exceptions import ItemError, ItemNotFoundError

if TYPE_CHECKING:
    from collections.abc import Generator
    from pathlib import Path


@dataclass
class EngagementAccountGroupings(BaseSet):
    @cached_property
    def base_url(self) -> str:
        return f"{self.server.base_url}/engagement-account-groupings"

    def get_by_id(self, id: str) -> EngagementAccountGroupingItem:
        url = f"{self.base_url}/{id}"
        resp_dict = super()._get_by_id(url=url)
        engagement_account_grouping = EngagementAccountGroupingItem.model_validate(
            resp_dict
        )
        self.restart_engagement_account_groups(engagement_account_grouping)
        return engagement_account_grouping

    def get(
        self, json: dict[str, Any] | None = None
    ) -> "Generator[EngagementAccountGroupingItem, None, None]":
        if json is None:
            json = {}

        url = f"{self.base_url}/query"
        for resp_dict in super()._get(url=url, json=json):
            engagement_account_grouping = EngagementAccountGroupingItem.model_validate(
                resp_dict
            )
            self.restart_engagement_account_groups(engagement_account_grouping)
            yield engagement_account_grouping

    def export(self, input_item: EngagementAccountGroupingItem) -> AsyncResultItem:
        if getattr(input_item, "id", None) is None:
            raise ItemNotFoundError

        url = f"{self.base_url}/{input_item.id}/export"
        resp_dict = super()._create(url=url)

        return AsyncResultItem.model_validate(resp_dict)

    def wait_for_export(
        self, async_result: AsyncResultItem, max_wait_minutes: int = 5
    ) -> None:
        """Wait for the async result for the data table export to complete.

        Waits, at most the minutes specified, for the async result to be COMPLETE and
        raises and error if any error

        Args:
            async_result (AsyncResultItem): Async result to check
            max_wait_minutes (int): Maximum minutes to wait (default: `5`)

        Raises:
            ItemError: If not a ACCOUNT_GROUPING_EXPORT
        """
        if async_result.type != AsyncResultType.ACCOUNT_GROUPING_EXPORT:
            msg = f"{async_result.type=}."
            raise ItemError(msg)

        self.server.async_results._wait_for_async_result(
            async_result=async_result,
            max_wait_minutes=max_wait_minutes,
            init_interval_sec=5,
        )

    def download(
        self, async_result: AsyncResultItem, output_file_path: "Path"
    ) -> "Path":
        if async_result.id is None:
            raise ItemNotFoundError

        async_result = self.server.async_results.get_by_id(async_result.id)

        file_result_id = async_result._get_file_result_id(
            expected_type=AsyncResultType.ACCOUNT_GROUPING_EXPORT
        )

        file_result = self.server.file_results.get_by_id(file_result_id)

        return self.server.file_results.export(
            file_result=file_result, output_file_path=output_file_path
        )

    def restart_engagement_account_groups(
        self, engagement_account_grouping: EngagementAccountGroupingItem
    ) -> None:
        if getattr(engagement_account_grouping, "id", None) is None:
            raise ItemNotFoundError

        engagement_account_grouping.engagement_account_groups = (
            self.server.engagement_account_groups.get(
                json={
                    "engagementAccountGroupingId": {
                        "$eq": engagement_account_grouping.id
                    }
                }
            )
        )
