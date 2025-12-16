#
#  Copyright MindBridge Analytics Inc. all rights reserved.
#
#  This material is confidential and may not be copied, distributed,
#  reversed engineered, decompiled or otherwise disseminated without
#  the prior written consent of MindBridge Analytics Inc.
#

from typing import Annotated
from pydantic import ConfigDict, Field, model_validator
from mindbridgeapi.common_validators import _warning_if_extra_fields
from mindbridgeapi.exceptions import ItemError
from mindbridgeapi.generated_pydantic_model.model import (
    ApiJoinVirtualColumnUpdate,
    ApiSplitByDelimiterVirtualColumnUpdate,
    ApiSplitByPositionVirtualColumnUpdate,
    ApiVirtualColumnUpdate,
    Type73 as _VirtualColumnType,
)

VirtualColumnType = _VirtualColumnType  # Match the type of VirtualColumn.type


class VirtualColumn(ApiVirtualColumnUpdate):
    """Virtual column.

    These are columns that are created in the Column Mapping step of the import process
    based on split, join, and duplicate actions.

    - column_index: Also in: ApiDuplicateVirtualColumn and
        ApiSplitByPositionVirtualColumnUpdate
    - delimiter: Also in ApiSplitByDelimiterVirtualColumnUpdate
    """

    column_index: Annotated[
        int | None,
        Field(
            alias=ApiSplitByDelimiterVirtualColumnUpdate.model_fields[
                "column_index"
            ].alias,
            description=ApiSplitByDelimiterVirtualColumnUpdate.model_fields[
                "column_index"
            ].description,
        ),
    ] = None
    split_index: Annotated[
        int | None,
        Field(
            alias=ApiSplitByDelimiterVirtualColumnUpdate.model_fields[
                "split_index"
            ].alias,
            description=ApiSplitByDelimiterVirtualColumnUpdate.model_fields[
                "split_index"
            ].description,
        ),
    ] = None
    column_indices: Annotated[
        list[int] | None,
        Field(
            alias=ApiJoinVirtualColumnUpdate.model_fields["column_indices"].alias,
            description=ApiJoinVirtualColumnUpdate.model_fields[
                "column_indices"
            ].description,
        ),
    ] = None
    delimiter: Annotated[
        str | None,
        Field(
            description=ApiJoinVirtualColumnUpdate.model_fields["delimiter"].description
        ),
    ] = None
    end_position: Annotated[
        int | None,
        Field(
            alias=ApiSplitByPositionVirtualColumnUpdate.model_fields[
                "end_position"
            ].alias,
            description=ApiSplitByPositionVirtualColumnUpdate.model_fields[
                "end_position"
            ].description,
        ),
    ] = None
    start_position: Annotated[
        int | None,
        Field(
            alias=ApiSplitByPositionVirtualColumnUpdate.model_fields[
                "start_position"
            ].alias,
            description=ApiSplitByPositionVirtualColumnUpdate.model_fields[
                "start_position"
            ].description,
        ),
    ] = None

    model_config = ConfigDict(
        extra="allow",
        validate_assignment=True,
        validate_default=True,
        validate_return=True,
    )
    _ = model_validator(mode="after")(_warning_if_extra_fields)

    @model_validator(mode="after")
    def try_to_determine_type(self) -> "VirtualColumn":
        if self.column_indices is not None and len(self.column_indices) == 0:
            self.column_indices = None

        if self.type is not None:
            return self

        if (
            self.column_index is not None
            and self.delimiter is None
            and self.column_indices is None
            and self.split_index is None
            and self.start_position is None
            and self.end_position is None
        ):
            self.type = VirtualColumnType.DUPLICATE
        elif (
            self.column_index is None
            and self.delimiter is not None
            and self.column_indices is not None
            and self.split_index is None
            and self.start_position is None
            and self.end_position is None
        ):
            self.type = VirtualColumnType.JOIN
        elif (
            self.column_index is not None
            and self.delimiter is not None
            and self.column_indices is None
            and self.split_index is not None
            and self.start_position is None
            and self.end_position is None
        ):
            self.type = VirtualColumnType.SPLIT_BY_DELIMITER
        elif (
            self.column_index is not None
            and self.delimiter is None
            and self.column_indices is None
            and self.split_index is None
            and self.start_position is not None
            and self.end_position is not None
        ):
            self.type = VirtualColumnType.SPLIT_BY_POSITION

        if self.type is None:
            msg = f"Unable to determine type of VirtualColumn: {self}."
            raise ItemError(msg)

        return self
