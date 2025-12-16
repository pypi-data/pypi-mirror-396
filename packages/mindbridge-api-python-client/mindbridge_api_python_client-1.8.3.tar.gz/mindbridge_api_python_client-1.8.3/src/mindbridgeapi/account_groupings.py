#
#  Copyright MindBridge Analytics Inc. all rights reserved.
#
#  This material is confidential and may not be copied, distributed,
#  reversed engineered, decompiled or otherwise disseminated without
#  the prior written consent of MindBridge Analytics Inc.
#

from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING, Any, Union
from mindbridgeapi.account_grouping_item import (
    AccountGroupingFileType,
    AccountGroupingItem,
)
from mindbridgeapi.async_result_item import AsyncResultItem, AsyncResultType
from mindbridgeapi.async_results import AsyncResults
from mindbridgeapi.base_set import BaseSet
from mindbridgeapi.exceptions import ItemError, ItemNotFoundError
from mindbridgeapi.generated_pydantic_model.model import (
    ApiImportAccountGroupingParamsCreate,
    ApiImportAccountGroupingParamsUpdate,
)

if TYPE_CHECKING:
    from collections.abc import Generator
    from os import PathLike
    from pathlib import Path


@dataclass
class AccountGroupings(BaseSet):
    def __post_init__(self) -> None:
        self.async_result_set = AsyncResults(server=self.server)

    @cached_property
    def base_url(self) -> str:
        return f"{self.server.base_url}/account-groupings"

    def get_by_id(self, id: str) -> AccountGroupingItem:
        url = f"{self.base_url}/{id}"
        resp_dict = super()._get_by_id(url=url)

        account_grouping = AccountGroupingItem.model_validate(resp_dict)
        self.restart_account_groups(account_grouping)
        return account_grouping

    def get(
        self, json: dict[str, Any] | None = None
    ) -> "Generator[AccountGroupingItem, None, None]":
        if json is None:
            json = {}

        url = f"{self.base_url}/query"
        for resp_dict in super()._get(url=url, json=json):
            account_grouping = AccountGroupingItem.model_validate(resp_dict)
            self.restart_account_groups(account_grouping)
            yield account_grouping

    def export(self, input_item: AccountGroupingItem) -> AsyncResultItem:
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

        self.async_result_set._wait_for_async_result(
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

    def upload(
        self,
        name: str,
        input_file: Union[str, "PathLike[Any]"],
        type: AccountGroupingFileType = AccountGroupingFileType.MINDBRIDGE_TEMPLATE,
    ) -> AccountGroupingItem:
        chunked_file = self.server.chunked_files.upload(input_file)

        url = f"{self.base_url}/import-from-chunked-file"
        ag_params = ApiImportAccountGroupingParamsCreate(
            name=name, type=type, chunked_file_id=chunked_file.id
        )
        json = ag_params.model_dump(mode="json", by_alias=True, exclude_none=True)
        resp_dict = super()._create(url=url, json=json)

        account_grouping = AccountGroupingItem.model_validate(resp_dict)
        self.restart_account_groups(account_grouping)
        return account_grouping

    def update(self, account_grouping: AccountGroupingItem) -> AccountGroupingItem:
        if getattr(account_grouping, "id", None) is None:
            raise ItemNotFoundError

        url = f"{self.base_url}/{account_grouping.id}"
        resp_dict = super()._update(url=url, json=account_grouping.update_json)

        account_grouping = AccountGroupingItem.model_validate(resp_dict)
        self.restart_account_groups(account_grouping)
        return account_grouping

    def delete(self, account_grouping: AccountGroupingItem) -> None:
        if getattr(account_grouping, "id", None) is None:
            raise ItemNotFoundError

        url = f"{self.base_url}/{account_grouping.id}"
        super()._delete(url=url)

    def append(
        self,
        account_grouping: AccountGroupingItem,
        input_file: Union[str, "PathLike[Any]"],
    ) -> AccountGroupingItem:
        chunked_file = self.server.chunked_files.upload(input_file)

        url = f"{self.base_url}/{account_grouping.id}/append-from-chunked-file"
        ag_params = ApiImportAccountGroupingParamsUpdate(
            chunked_file_id=chunked_file.id
        )
        json = ag_params.model_dump(mode="json", by_alias=True, exclude_none=True)
        resp_dict = super()._create(url=url, json=json)

        account_grouping = AccountGroupingItem.model_validate(resp_dict)
        self.restart_account_groups(account_grouping)
        return account_grouping

    def restart_account_groups(self, account_grouping: AccountGroupingItem) -> None:
        if getattr(account_grouping, "id", None) is None:
            raise ItemNotFoundError

        account_grouping.account_groups = self.server.account_groups.get(
            json={"accountGroupingId": {"$eq": account_grouping.id}}
        )
