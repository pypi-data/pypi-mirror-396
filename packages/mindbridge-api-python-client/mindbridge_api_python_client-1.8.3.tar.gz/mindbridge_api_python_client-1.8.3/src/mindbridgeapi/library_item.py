#
#  Copyright MindBridge Analytics Inc. all rights reserved.
#
#  This material is confidential and may not be copied, distributed,
#  reversed engineered, decompiled or otherwise disseminated without
#  the prior written consent of MindBridge Analytics Inc.
#

from collections.abc import Generator
from typing import Annotated, Any, ClassVar
from pydantic import ConfigDict, Field, field_validator, model_validator
from mindbridgeapi.analysis_type_item import AnalysisTypeItem
from mindbridgeapi.common_validators import (
    _convert_userinfo_to_useritem,
    _warning_if_extra_fields,
)
from mindbridgeapi.generated_pydantic_model.model import (
    ApiLibraryCreate,
    ApiLibraryRead,
    ApiLibraryUpdate,
    RiskScoreDisplay,
)


def _empty_analysis_types() -> Generator[AnalysisTypeItem, None, None]:
    """Empty generator function.

    This returns an empty generator function, it's use is to ensure analysis_types is
    not None for the LibraryItem class

    Yields:
        AnalysisTypeItem: Will never yield anything
    """
    yield from ()


class LibraryItem(ApiLibraryRead):
    """Represents a specific Library.

    ```py
    import os
    import mindbridgeapi as mbapi

    server = mbapi.Server(
        url=os.environ["MINDBRIDGE_API_TEST_URL"],
        token=os.environ["MINDBRIDGE_API_TEST_TOKEN"],
    )
    account_grouping = next(
        x
        for x in server.account_groupings.get()
        if x.system and x.name.get("en") == "MAC v.2"
    )
    library = mbapi.LibraryItem(
        name="My Library Name", account_grouping_id=account_grouping.id
    )
    ```

    Attributes:
        id (str): The unique object identifier.
        name (str): The current name of the library.
        based_on_library_id (str): Identifies the library that the new library is based
            on. This may be a user-created library or a MindBridge system library.
            (default: `LibraryItem.MINDBRIDGE_FOR_PROFIT`)
        analysis_type_ids (list[str]]): Identifies the analysis types used in the
            library. (default: `[AnalysisTypeItem.GENERAL_LEDGER]`)
        account_grouping_id (str): Identifies the account grouping used.
        risk_score_display (RiskScoreDisplay): Determines whether risk scores will be
            presented as percentages (%), or using High, Medium, and Low label
            indicators. (default: `RiskScoreDisplay.PERCENTAGE`)
        control_point_selection_permission (bool): When set to `true`, control points
            can be added or removed within each risk score. (default: `True`)
        control_point_weight_permission (bool): When set to `true`, the weight of each
            control point can be adjusted within each risk score. (default: `True`)
        control_point_settings_permission (bool): When set to `true`, individual control
            point settings can be adjusted within each risk score. (default: `True`)
        risk_score_and_groups_selection_permission (bool): When set to `true`, risk
            scores and groups can be disabled, and accounts associated with risk scores
            can be edited. (default: `True`)
        default_delimiter (str): Identifies the default delimiter used in imported CSV
            files.
        risk_range_edit_permission (bool): (default: `True`)
        convert_settings (bool): Indicates whether or not settings from the selected
            base library should be converted for use with the selected account grouping.
        warnings_dismissed (bool): When set to `true`, any conversion warnings for this
            library will not be displayed in the **Libraries** tab in the UI.
        archived (bool): Indicates whether or not the library is archived. Archived
            libraries cannot be selected when creating an engagement.
        system (bool): Indicates whether or not the library is a MindBridge system
            library.
        original_system_library_id (str): Identifies the original MindBridge-supplied
            library.
        conversion_warnings (list[ProblemRead]]): A list of accounts that failed to
            convert the selected base library's setting to the selected account
            grouping.
    """

    MINDBRIDGE_FOR_PROFIT: ClassVar[str] = "5cc9076887f13cb8a7a1926b"
    MINDBRIDGE_NOT_FOR_PROFIT: ClassVar[str] = "5cc90bbd87f13cb8a7a1926d"
    MINDBRIDGE_NOT_FOR_PROFIT_WITH_FUNDS: ClassVar[str] = "5cc90b8f87f13cb8a7a1926c"
    MINDBRIDGE_REVIEW: ClassVar[str] = "5f2c22489db6c9ff301b16cb"
    based_on_library_id: Annotated[
        str,
        Field(
            alias=ApiLibraryRead.model_fields["based_on_library_id"].alias,
            description=ApiLibraryRead.model_fields["based_on_library_id"].description,
        ),
    ] = MINDBRIDGE_FOR_PROFIT
    analysis_type_ids: Annotated[
        list[str],
        Field(
            alias=ApiLibraryRead.model_fields["analysis_type_ids"].alias,
            description=ApiLibraryRead.model_fields["analysis_type_ids"].description,
        ),
    ] = [AnalysisTypeItem.GENERAL_LEDGER]  # noqa: RUF012
    risk_score_display: Annotated[
        RiskScoreDisplay,
        Field(
            alias=ApiLibraryRead.model_fields["risk_score_display"].alias,
            description=ApiLibraryRead.model_fields["risk_score_display"].description,
        ),
    ] = RiskScoreDisplay.PERCENTAGE
    control_point_selection_permission: Annotated[
        bool,
        Field(
            alias=ApiLibraryRead.model_fields[
                "control_point_selection_permission"
            ].alias,
            description=ApiLibraryRead.model_fields[
                "control_point_selection_permission"
            ].description,
        ),
    ] = True
    control_point_weight_permission: Annotated[
        bool,
        Field(
            alias=ApiLibraryRead.model_fields["control_point_weight_permission"].alias,
            description=ApiLibraryRead.model_fields[
                "control_point_weight_permission"
            ].description,
        ),
    ] = True
    control_point_settings_permission: Annotated[
        bool,
        Field(
            alias=ApiLibraryRead.model_fields[
                "control_point_settings_permission"
            ].alias,
            description=ApiLibraryRead.model_fields[
                "control_point_settings_permission"
            ].description,
        ),
    ] = True
    risk_score_and_groups_selection_permission: Annotated[
        bool,
        Field(
            alias=ApiLibraryRead.model_fields[
                "risk_score_and_groups_selection_permission"
            ].alias,
            description=ApiLibraryRead.model_fields[
                "risk_score_and_groups_selection_permission"
            ].description,
        ),
    ] = True
    risk_range_edit_permission: Annotated[
        bool,
        Field(alias=ApiLibraryRead.model_fields["risk_range_edit_permission"].alias),
    ] = True
    analysis_types: Annotated[
        Generator[AnalysisTypeItem, None, None], Field(exclude=True)
    ] = _empty_analysis_types()

    model_config = ConfigDict(
        extra="allow",
        validate_assignment=True,
        validate_default=True,
        validate_return=True,
    )
    _a = model_validator(mode="after")(_warning_if_extra_fields)
    _b = field_validator("*")(_convert_userinfo_to_useritem)

    def _get_post_json(
        self, out_class: type[ApiLibraryCreate | ApiLibraryUpdate]
    ) -> dict[str, Any]:
        in_class_dict = self.model_dump()
        out_class_object = out_class.model_validate(in_class_dict)
        return out_class_object.model_dump(
            mode="json", by_alias=True, exclude_none=True
        )

    @property
    def create_json(self) -> dict[str, Any]:
        return self._get_post_json(out_class=ApiLibraryCreate)

    @property
    def update_json(self) -> dict[str, Any]:
        return self._get_post_json(out_class=ApiLibraryUpdate)
