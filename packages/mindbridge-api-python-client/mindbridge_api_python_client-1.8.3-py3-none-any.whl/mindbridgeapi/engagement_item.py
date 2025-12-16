#
#  Copyright MindBridge Analytics Inc. all rights reserved.
#
#  This material is confidential and may not be copied, distributed,
#  reversed engineered, decompiled or otherwise disseminated without
#  the prior written consent of MindBridge Analytics Inc.
#

from collections.abc import Generator
from datetime import date, datetime, timezone
from typing import Annotated, Any
from pydantic import ConfigDict, Field, field_validator, model_validator
from mindbridgeapi.accounting_period import AccountingPeriod
from mindbridgeapi.analysis_item import AnalysisItem
from mindbridgeapi.common_validators import (
    _convert_userinfo_to_useritem,
    _warning_if_extra_fields,
)
from mindbridgeapi.engagement_account_grouping_item import EngagementAccountGroupingItem
from mindbridgeapi.file_manager_item import FileManagerItem
from mindbridgeapi.generated_pydantic_model.model import (
    ApiEngagementCreate,
    ApiEngagementRead,
    ApiEngagementUpdate,
)
from mindbridgeapi.library_item import LibraryItem


def _empty_analyses() -> Generator[AnalysisItem, None, None]:
    """Empty generator function.

    This returns an empty generator function, it's use is to ensure analyses is not None
    for the EngagementItem class

    Yields:
        AnalysisItem: Will never yield anything
    """
    yield from ()


def _empty_file_manager_items() -> Generator[FileManagerItem, None, None]:
    """Empty generator function.

    This returns an empty generator function, it's use is to ensure file_manager_items
    is not None for the EngagementItem class

    Yields:
        FileManagerItem: Will never yield anything
    """
    yield from ()


def _empty_engagement_account_groupings() -> Generator[
    EngagementAccountGroupingItem, None, None
]:
    """Empty generator function.

    This returns an empty generator function, it's use is to ensure
    engagement_account_groupings is not None for the EngagementAccountGroupingItem class

    Yields:
        EngagementAccountGroupingItem: Will never yield anything
    """
    yield from ()


class EngagementItem(ApiEngagementRead):
    accounting_package: Annotated[
        str,
        Field(
            alias=ApiEngagementRead.model_fields["accounting_package"].alias,
            description=ApiEngagementRead.model_fields[
                "accounting_package"
            ].description,
        ),
    ] = "Other"
    accounting_period: Annotated[
        AccountingPeriod,
        Field(
            alias=ApiEngagementRead.model_fields["accounting_period"].alias,
            description=ApiEngagementRead.model_fields["accounting_period"].description,
        ),
    ] = AccountingPeriod()
    audit_period_end_date: Annotated[
        date,
        Field(
            alias=ApiEngagementRead.model_fields["audit_period_end_date"].alias,
            description=ApiEngagementRead.model_fields[
                "audit_period_end_date"
            ].description,
        ),
    ] = datetime.now(tz=timezone.utc).astimezone().date().replace(month=12, day=31)
    industry: Annotated[
        str, Field(description=ApiEngagementRead.model_fields["industry"].description)
    ] = "Other"
    library_id: Annotated[
        str,
        Field(
            alias=ApiEngagementRead.model_fields["library_id"].alias,
            description=ApiEngagementRead.model_fields["library_id"].description,
        ),
    ] = LibraryItem.MINDBRIDGE_FOR_PROFIT
    settings_based_on_engagement_id: Annotated[
        str | None,
        Field(
            alias=ApiEngagementCreate.model_fields[
                "settings_based_on_engagement_id"
            ].alias,
            description=ApiEngagementCreate.model_fields[
                "settings_based_on_engagement_id"
            ].description,
        ),
    ] = None
    file_manager_items: Annotated[
        Generator[FileManagerItem, None, None], Field(exclude=True)
    ] = _empty_file_manager_items()
    analyses: Annotated[Generator[AnalysisItem, None, None], Field(exclude=True)] = (
        _empty_analyses()
    )
    engagement_account_groupings: Annotated[
        Generator[EngagementAccountGroupingItem, None, None], Field(exclude=True)
    ] = _empty_engagement_account_groupings()

    model_config = ConfigDict(
        extra="allow",
        validate_assignment=True,
        validate_default=True,
        validate_return=True,
    )
    _a = model_validator(mode="after")(_warning_if_extra_fields)
    _b = field_validator("*")(_convert_userinfo_to_useritem)

    def _get_post_json(
        self, out_class: type[ApiEngagementCreate | ApiEngagementUpdate]
    ) -> dict[str, Any]:
        in_class_dict = self.model_dump()
        out_class_object = out_class.model_validate(in_class_dict)
        return out_class_object.model_dump(
            mode="json", by_alias=True, exclude_none=True
        )

    @property
    def create_json(self) -> dict[str, Any]:
        return self._get_post_json(out_class=ApiEngagementCreate)

    @property
    def update_json(self) -> dict[str, Any]:
        return self._get_post_json(out_class=ApiEngagementUpdate)
