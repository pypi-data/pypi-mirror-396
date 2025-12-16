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
from mindbridgeapi.analyses import Analyses
from mindbridgeapi.async_result_item import AsyncResultItem, AsyncResultType
from mindbridgeapi.base_set import BaseSet
from mindbridgeapi.engagement_item import EngagementItem
from mindbridgeapi.exceptions import (
    ItemAlreadyExistsError,
    ItemError,
    ItemNotFoundError,
)
from mindbridgeapi.file_manager import FileManager

if TYPE_CHECKING:
    from collections.abc import Generator
    from pathlib import Path


@dataclass
class Engagements(BaseSet):
    @cached_property
    def base_url(self) -> str:
        return f"{self.server.base_url}/engagements"

    def create(self, item: EngagementItem) -> EngagementItem:
        if getattr(item, "id", None) is not None and item.id is not None:
            raise ItemAlreadyExistsError(item.id)

        url = self.base_url
        resp_dict = super()._create(url=url, json=item.create_json)
        engagement = EngagementItem.model_validate(resp_dict)
        return self._restart_all_children(engagement)

    def get_by_id(self, id: str) -> EngagementItem:
        url = f"{self.base_url}/{id}"
        resp_dict = super()._get_by_id(url=url)
        engagement = EngagementItem.model_validate(resp_dict)
        return self._restart_all_children(engagement)

    def update(self, item: EngagementItem) -> EngagementItem:
        if getattr(item, "id", None) is None:
            raise ItemNotFoundError

        url = f"{self.base_url}/{item.id}"
        resp_dict = super()._update(url=url, json=item.update_json)

        engagement = EngagementItem.model_validate(resp_dict)
        return self._restart_all_children(engagement)

    def get(
        self, json: dict[str, Any] | None = None
    ) -> "Generator[EngagementItem, None, None]":
        if json is None:
            json = {}

        url = f"{self.base_url}/query"
        for resp_dict in super()._get(url=url, json=json):
            engagement = EngagementItem.model_validate(resp_dict)
            yield self._restart_all_children(engagement)

    def restart_file_manager_items(self, engagement_item: EngagementItem) -> None:
        if getattr(engagement_item, "id", None) is None:
            raise ItemNotFoundError

        engagement_item.file_manager_items = FileManager(server=self.server).get(
            json={"engagementId": {"$eq": engagement_item.id}}
        )

    def restart_analyses(self, engagement_item: EngagementItem) -> None:
        if getattr(engagement_item, "id", None) is None:
            raise ItemNotFoundError

        engagement_item.analyses = Analyses(server=self.server).get(
            json={"engagementId": {"$eq": engagement_item.id}}
        )

    def delete(self, item: EngagementItem) -> None:
        if getattr(item, "id", None) is None:
            raise ItemNotFoundError

        url = f"{self.base_url}/{item.id}"
        super()._delete(url=url)

    def restart_engagement_account_groupings(self, engagement: EngagementItem) -> None:
        if getattr(engagement, "id", None) is None:
            raise ItemNotFoundError

        engagement.engagement_account_groupings = (
            self.server.engagement_account_groupings.get(
                json={"engagementId": {"$eq": engagement.id}}
            )
        )

    def _restart_all_children(self, engagement: EngagementItem) -> EngagementItem:
        self.restart_file_manager_items(engagement)
        self.restart_analyses(engagement)
        self.restart_engagement_account_groupings(engagement)

        return engagement

    def delete_unused_account_mappings(
        self, engagement: EngagementItem
    ) -> EngagementItem:
        if engagement.id is None:
            raise ItemNotFoundError

        url = f"{self.server.account_mappings.base_url}/delete-unused"
        json = {"engagementId": engagement.id}
        _ = super()._create(url=url, json=json)

        return self.get_by_id(engagement.id)

    def export_account_mappings(self, engagement: EngagementItem) -> AsyncResultItem:
        if engagement.id is None:
            raise ItemNotFoundError

        url = f"{self.server.account_mappings.base_url}/export"
        json = {"engagementId": engagement.id}
        resp_dict = super()._create(url=url, json=json)

        return AsyncResultItem.model_validate(resp_dict)

    def account_mappings_wait_for_export(
        self, async_result: AsyncResultItem, max_wait_minutes: int = 5
    ) -> None:
        """Wait for the async result for the data table export to complete.

        Waits, at most the minutes specified, for the async result to be COMPLETE and
        raises and error if any error

        Args:
            async_result (AsyncResultItem): Async result to check
            max_wait_minutes (int): Maximum minutes to wait (default: `5`)

        Raises:
            ItemError: If not a ACCOUNT_MAPPING_EXPORT
        """
        if async_result.type != AsyncResultType.ACCOUNT_MAPPING_EXPORT:
            msg = f"{async_result.type=}."
            raise ItemError(msg)

        self.server.async_results._wait_for_async_result(
            async_result=async_result,
            max_wait_minutes=max_wait_minutes,
            init_interval_sec=5,
        )

    def download_account_mappings(
        self, async_result: AsyncResultItem, output_file_path: "Path"
    ) -> "Path":
        if async_result.id is None:
            raise ItemNotFoundError

        file_result_id = async_result._get_file_result_id(
            expected_type=AsyncResultType.ACCOUNT_MAPPING_EXPORT
        )

        file_result = self.server.file_results.get_by_id(file_result_id)

        return self.server.file_results.export(
            file_result=file_result, output_file_path=output_file_path
        )

    def verify_account_mappings(self, engagement: EngagementItem) -> EngagementItem:
        if engagement.id is None:
            raise ItemNotFoundError

        url = f"{self.server.account_mappings.base_url}/verify"
        json = {"engagementId": engagement.id}
        _ = super()._create(url=url, json=json)

        return self.get_by_id(engagement.id)
