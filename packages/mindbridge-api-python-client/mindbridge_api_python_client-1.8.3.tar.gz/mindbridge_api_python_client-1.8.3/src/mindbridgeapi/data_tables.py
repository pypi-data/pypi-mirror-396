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
from pydantic import BaseModel, model_validator
from mindbridgeapi.async_result_item import AsyncResultItem, AsyncResultType
from mindbridgeapi.async_results import AsyncResults
from mindbridgeapi.base_set import BaseSet, PageLocation
from mindbridgeapi.common_validators import _convert_json_query
from mindbridgeapi.exceptions import ItemError, ItemNotFoundError
from mindbridgeapi.generated_pydantic_model.model import (
    ApiDataTableExportRequest,
    ApiDataTableQueryRead,
    ApiDataTableQuerySortOrderRead,
    ApiDataTableRead,
    Direction,
    Type6 as DataTableColumnType,  # Match the type of ApiDataTableColumnRead.type
)

if TYPE_CHECKING:
    from collections.abc import Generator
    from pathlib import Path


class _DataTableQueryValidator(BaseModel):
    """Help validate and set defaults.

    ApiDataTableQueryRead and ApiDataTableExportRequest are the same for our purposes.

    Attributes:
        data_table: Only columns and logical_name are used for reference.
        data_table_query: sort is updated with some defaults.
    """

    data_table: ApiDataTableRead
    data_table_query: ApiDataTableQueryRead

    @model_validator(mode="after")
    def set_sort_field(self) -> "_DataTableQueryValidator":
        if not self.data_table.id:
            raise ItemNotFoundError

        if not self.data_table.columns:
            msg = f"{self.data_table.columns=}."
            raise ItemError(msg)

        if not self.data_table_query.sort:
            self.data_table_query.sort = ApiDataTableQuerySortOrderRead()

        if not self.data_table_query.sort.direction:
            self.data_table_query.sort.direction = Direction.ASC

        if (
            not self.data_table_query.sort.field
            and self.data_table.logical_name == "gl_journal_lines"
            and ("rowid" in (x.field for x in self.data_table.columns))
        ):
            self.data_table_query.sort.field = "rowid"
        elif (
            not self.data_table_query.sort.field
            and self.data_table.logical_name == "gl_journal_tx"
            and ("txid" in (x.field for x in self.data_table.columns))
        ):
            self.data_table_query.sort.field = "txid"
        else:
            self.data_table_query.sort = None

        return self


@dataclass
class DataTables(BaseSet):
    def __post_init__(self) -> None:
        self.async_result_set = AsyncResults(server=self.server)

    @cached_property
    def base_url(self) -> str:
        return f"{self.server.base_url}/data-tables"

    def get_table_data(
        self,
        data_table_item: ApiDataTableRead,
        fields: list[str] | None = None,
        query: dict[str, Any] | None = None,
        sort_field: str | None = None,
        sort_direction: Direction = Direction.ASC,
    ) -> "Generator[dict[str, Any], None, None]":
        """Query Data Table Data.

        Args:
            data_table_item (ApiDataTableRead): Data table to get table data for
            fields (list[str]): Fields to include in the output, default is all fields
            query (dict[str, Any]): Query parameters for filtering the data table data,
                default is no filter
            sort_field (str): Field to sort by, default may be applied based on the data
                table
            sort_direction (Direction): Ascending or Decedning on sort_field
        """
        data_table_query_validator = _DataTableQueryValidator(
            data_table=data_table_item,
            data_table_query=ApiDataTableQueryRead(
                fields=self._export_get_fields(
                    input_item=data_table_item, fields=fields
                ),
                sort=ApiDataTableQuerySortOrderRead(
                    field=sort_field, direction=sort_direction
                ),
            ),
        )

        json = data_table_query_validator.data_table_query.model_dump(
            mode="json", by_alias=True, exclude_none=True
        )
        json["query"] = _convert_json_query(query)

        yield from super()._get(
            url=f"{self.base_url}/{data_table_query_validator.data_table.id}/data",
            json=json,
            page_location=PageLocation.REQUEST_BODY,
            try_again_if_locked=True,
        )

    def get_by_id(self, id: str) -> ApiDataTableRead:
        url = f"{self.base_url}/{id}"
        resp_dict = super()._get_by_id(url=url)

        return ApiDataTableRead.model_validate(resp_dict)

    def get(
        self, json: dict[str, Any] | None = None
    ) -> "Generator[ApiDataTableRead, None, None]":
        mb_query_dict = _convert_json_query(json, required_key="analysisId")

        url = f"{self.base_url}/query"
        for resp_dict in super()._get(url=url, json=mb_query_dict):
            yield ApiDataTableRead.model_validate(resp_dict)

    @staticmethod
    def _export_get_fields(
        input_item: ApiDataTableRead, fields: list[str] | None = None
    ) -> list[str]:
        if fields:
            return fields

        if not input_item.columns:
            return []

        """
        "KEYWORD_SEARCH columns can't be included in data table exports. Attempting to
            select them as part of fields will cause the export request to fail.".
            Similarly fields that are filter only can't be included as fields.
        """
        return [
            x.field
            for x in input_item.columns
            if x.type != DataTableColumnType.KEYWORD_SEARCH
            and x.field is not None
            and not x.filter_only
        ]

    def export(  # noqa: PLR0913
        self,
        input_item: ApiDataTableRead,
        fields: list[str] | None = None,
        query: dict[str, Any] | None = None,
        limit: int | None = None,
        sort_direction: Direction | None = None,
        sort_field: str | None = None,
    ) -> AsyncResultItem:
        """Export Data Table.

        Creates a asynchronous background job that can be downloaded once done.

        Args:
            input_item (ApiDataTableRead): Data table to get table data for
            fields (list[str]): Fields to include in the output, default is all fields
            query (dict[str, Any]): Query parameters for filtering the data table data,
                default is no filter
            limit (int): Limit the number of rows in the data table export (default:
                `None`)
            sort_direction (Direction): Ascending or Decedning on sort_field
            sort_field (str): Field to sort by, default may be applied based on the data
                table

        Returns:
            AsyncResultItem: Async result to be used to track the status of the
                asynchronous background job
        """
        data_table_query_validator = _DataTableQueryValidator(
            data_table=input_item,
            data_table_query=ApiDataTableQueryRead(
                fields=self._export_get_fields(input_item=input_item, fields=fields),
                sort=ApiDataTableQuerySortOrderRead(
                    field=sort_field, direction=sort_direction
                ),
            ),
        )

        data_table_export_request = ApiDataTableExportRequest.model_validate(
            data_table_query_validator.data_table_query.model_dump(exclude_none=True)
        )
        data_table_export_request.limit = limit

        json = data_table_export_request.model_dump(
            mode="json", by_alias=True, exclude_none=True
        )
        json["query"] = _convert_json_query(query)

        resp_dict = super()._create(
            url=f"{self.base_url}/{input_item.id}/export", json=json
        )

        return AsyncResultItem.model_validate(resp_dict)

    def wait_for_export(
        self, async_result: AsyncResultItem, max_wait_minutes: int = (24 * 60)
    ) -> None:
        """Wait for the async result for the data table export to complete.

        Waits, at most the minutes specified, for the async result to be COMPLETE and
        raises and error if any error

        Args:
            async_result (AsyncResultItem): Async result to check
            max_wait_minutes (int): Maximum minutes to wait (default: `24 * 60`)

        Raises:
            ItemError: If not a DATA_TABLE_EXPORT
        """
        if async_result.type != AsyncResultType.DATA_TABLE_EXPORT:
            msg = f"{async_result.type=}."
            raise ItemError(msg)

        self.async_result_set._wait_for_async_result(
            async_result=async_result,
            max_wait_minutes=max_wait_minutes,
            init_interval_sec=10,
        )

    def download(
        self, async_result: AsyncResultItem, output_file_path: "Path"
    ) -> "Path":
        if async_result.id is None:
            raise ItemNotFoundError

        async_result = self.server.async_results.get_by_id(async_result.id)

        file_result_id = async_result._get_file_result_id(
            expected_type=AsyncResultType.DATA_TABLE_EXPORT
        )

        file_result = self.server.file_results.get_by_id(file_result_id)

        return self.server.file_results.export(
            file_result=file_result, output_file_path=output_file_path
        )
