#
#  Copyright MindBridge Analytics Inc. all rights reserved.
#
#  This material is confidential and may not be copied, distributed,
#  reversed engineered, decompiled or otherwise disseminated without
#  the prior written consent of MindBridge Analytics Inc.
#

from typing import Annotated, Any, Literal
from pydantic import ConfigDict, Field, field_validator, model_validator
from mindbridgeapi.analysis_source_type_item import AnalysisSourceTypeItem
from mindbridgeapi.common_validators import (
    _convert_userinfo_to_useritem,
    _warning_if_extra_fields,
)
from mindbridgeapi.generated_pydantic_model.model import (
    ApiAnalysisSourceCreate,
    ApiAnalysisSourceRead,
    ApiAnalysisSourceUpdate,
    ApiDuplicateVirtualColumnUpdate,
    ApiJoinVirtualColumnUpdate,
    ApiSplitByDelimiterVirtualColumnUpdate,
    ApiSplitByPositionVirtualColumnUpdate,
)
from mindbridgeapi.virtual_column import VirtualColumn, VirtualColumnType


class DuplicateVirtualColumn(ApiDuplicateVirtualColumnUpdate):
    name: Annotated[
        str | None,
        Field(
            description=ApiDuplicateVirtualColumnUpdate.model_fields["name"].description
        ),
    ] = None  # type: ignore[assignment]
    type: Annotated[
        Literal[VirtualColumnType.DUPLICATE],
        Field(
            description=ApiDuplicateVirtualColumnUpdate.model_fields["type"].description
        ),
    ]
    version: Annotated[
        int | None,
        Field(
            description=ApiDuplicateVirtualColumnUpdate.model_fields[
                "version"
            ].description
        ),
    ] = None  # type: ignore[assignment]


class SplitByPositionVirtualColumn(ApiSplitByPositionVirtualColumnUpdate):
    name: Annotated[
        str | None,
        Field(
            description=ApiSplitByPositionVirtualColumnUpdate.model_fields[
                "name"
            ].description
        ),
    ] = None  # type: ignore[assignment]
    type: Annotated[
        Literal[VirtualColumnType.SPLIT_BY_POSITION],
        Field(
            description=ApiSplitByPositionVirtualColumnUpdate.model_fields[
                "type"
            ].description
        ),
    ]
    version: Annotated[
        int | None,
        Field(
            description=ApiSplitByPositionVirtualColumnUpdate.model_fields[
                "version"
            ].description
        ),
    ] = None  # type: ignore[assignment]


class SplitByDelimiterVirtualColumn(ApiSplitByDelimiterVirtualColumnUpdate):
    name: Annotated[
        str | None,
        Field(
            description=ApiSplitByDelimiterVirtualColumnUpdate.model_fields[
                "name"
            ].description
        ),
    ] = None  # type: ignore[assignment]
    type: Annotated[
        Literal[VirtualColumnType.SPLIT_BY_DELIMITER],
        Field(
            description=ApiSplitByDelimiterVirtualColumnUpdate.model_fields[
                "type"
            ].description
        ),
    ]
    version: Annotated[
        int | None,
        Field(
            description=ApiSplitByDelimiterVirtualColumnUpdate.model_fields[
                "version"
            ].description
        ),
    ] = None  # type: ignore[assignment]


class JoinVirtualColumn(ApiJoinVirtualColumnUpdate):
    name: Annotated[
        str | None,
        Field(description=ApiJoinVirtualColumnUpdate.model_fields["name"].description),
    ] = None  # type: ignore[assignment]
    type: Annotated[
        Literal[VirtualColumnType.JOIN],
        Field(description=ApiJoinVirtualColumnUpdate.model_fields["type"].description),
    ]
    version: Annotated[
        int | None,
        Field(
            description=ApiJoinVirtualColumnUpdate.model_fields["version"].description
        ),
    ] = None  # type: ignore[assignment]


_VirtualColumn = Annotated[
    DuplicateVirtualColumn
    | SplitByPositionVirtualColumn
    | SplitByDelimiterVirtualColumn
    | JoinVirtualColumn,
    Field(discriminator="type"),
]


class _ApiAnalysisSourceCreate(ApiAnalysisSourceCreate):
    """An Analysis Source in MindBridge for creation.

    proposed_virtual_columns is "overridden" so that it's able to determine the
        appropriate virtual column type.
    """

    proposed_virtual_columns: Annotated[
        list[_VirtualColumn] | None,
        Field(
            alias=ApiAnalysisSourceCreate.model_fields[
                "proposed_virtual_columns"
            ].alias,
            description=ApiAnalysisSourceCreate.model_fields[
                "proposed_virtual_columns"
            ].description,
        ),
    ] = None  # type: ignore[assignment]


class _ApiAnalysisSourceUpdate(ApiAnalysisSourceUpdate):
    """An Analysis Source in MindBridge for updating.

    proposed_virtual_columns and virtual_columns are "overridden" so that it's able to
        determine the appropriate virtual column type.
    """

    proposed_virtual_columns: Annotated[
        list[_VirtualColumn] | None,
        Field(
            alias=ApiAnalysisSourceUpdate.model_fields[
                "proposed_virtual_columns"
            ].alias,
            description=ApiAnalysisSourceUpdate.model_fields[
                "proposed_virtual_columns"
            ].description,
        ),
    ] = None  # type: ignore[assignment]
    virtual_columns: Annotated[
        list[_VirtualColumn] | None,
        Field(
            alias=ApiAnalysisSourceUpdate.model_fields["virtual_columns"].alias,
            description=ApiAnalysisSourceUpdate.model_fields[
                "virtual_columns"
            ].description,
        ),
    ] = None  # type: ignore[assignment]


class AnalysisSourceItem(ApiAnalysisSourceRead):
    """An Analysis Source in MindBridge.

    proposed_virtual_columns and virtual_columns are "overridden" so that it's able to
        determine the appropriate virtual column type.
    """

    analysis_source_type_id: Annotated[
        str,
        Field(
            alias=ApiAnalysisSourceRead.model_fields["analysis_source_type_id"].alias,
            description=ApiAnalysisSourceRead.model_fields[
                "analysis_source_type_id"
            ].description,
        ),
    ] = AnalysisSourceTypeItem.GENERAL_LEDGER_JOURNAL
    proposed_virtual_columns: Annotated[
        list[_VirtualColumn] | None,
        Field(
            alias=ApiAnalysisSourceRead.model_fields["proposed_virtual_columns"].alias,
            description=ApiAnalysisSourceRead.model_fields[
                "proposed_virtual_columns"
            ].description,
        ),
    ] = None  # type: ignore[assignment]
    virtual_columns: Annotated[
        list[_VirtualColumn] | None,
        Field(
            alias=ApiAnalysisSourceRead.model_fields["virtual_columns"].alias,
            description=ApiAnalysisSourceRead.model_fields[
                "virtual_columns"
            ].description,
        ),
    ] = None  # type: ignore[assignment]
    warnings_ignored: Annotated[
        bool,
        Field(
            alias=ApiAnalysisSourceRead.model_fields["warnings_ignored"].alias,
            description=ApiAnalysisSourceRead.model_fields[
                "warnings_ignored"
            ].description,
        ),
    ] = True

    model_config = ConfigDict(
        extra="allow",
        validate_assignment=True,
        validate_default=True,
        validate_return=True,
    )
    _a = model_validator(mode="after")(_warning_if_extra_fields)
    _b = field_validator("*")(_convert_userinfo_to_useritem)

    @field_validator("proposed_virtual_columns", mode="before")
    @classmethod
    def _convert_virtualcolumn_to_dict(cls, v: Any) -> Any:
        """Ensures virtualcolumns are parsed as the appropriate type.

        Returns:
            List of VirtualColumns as dicts.
        """
        if not isinstance(v, list):
            return v

        new_list = []
        for x in v:
            if isinstance(x, VirtualColumn):
                new_list.append(x.model_dump(by_alias=True, exclude_none=True))
            else:
                new_list.append(x)

        return new_list

    def _get_post_json(
        self, out_class: type[_ApiAnalysisSourceCreate | _ApiAnalysisSourceUpdate]
    ) -> dict[str, Any]:
        in_class_dict = self.model_dump()
        out_class_object = out_class.model_validate(in_class_dict)
        return out_class_object.model_dump(
            mode="json", by_alias=True, exclude_none=True
        )

    @property
    def create_json(self) -> dict[str, Any]:
        return self._get_post_json(out_class=_ApiAnalysisSourceCreate)

    @property
    def update_json(self) -> dict[str, Any]:
        return self._get_post_json(out_class=_ApiAnalysisSourceUpdate)
