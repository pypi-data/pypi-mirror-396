#
#  Copyright MindBridge Analytics Inc. all rights reserved.
#
#  This material is confidential and may not be copied, distributed,
#  reversed engineered, decompiled or otherwise disseminated without
#  the prior written consent of MindBridge Analytics Inc.
#

from typing import Any
from pydantic import ConfigDict, Field, field_validator, model_validator
from mindbridgeapi.common_validators import (
    _convert_userinfo_to_useritem,
    _warning_if_extra_fields,
)
from mindbridgeapi.filter_group_condition_item import FilterGroupConditionItem
from mindbridgeapi.generated_pydantic_model.model import (
    ApiPopulationTagCreate,
    ApiPopulationTagRead,
    ApiPopulationTagUpdate,
)


class PopulationItemCreate(ApiPopulationTagCreate):
    """Used internally when creating a Population Item."""

    condition: FilterGroupConditionItem | None = Field().merge_field_infos(
        ApiPopulationTagCreate.model_fields["condition"]
    )  # type: ignore[assignment]


class PopulationItemUpdate(ApiPopulationTagUpdate):
    """Used internally when updating a Population Item."""

    condition: FilterGroupConditionItem | None = Field().merge_field_infos(
        ApiPopulationTagUpdate.model_fields["condition"]
    )  # type: ignore[assignment]


class PopulationItem(ApiPopulationTagRead):
    """Represents a specific MindBridge Population.

    ```py
    from datetime import date
    import os
    import mindbridgeapi as mbapi

    server = mbapi.Server(
        url=os.environ["MINDBRIDGE_API_TEST_URL"],
        token=os.environ["MINDBRIDGE_API_TEST_TOKEN"],
    )
    analysis_result = next(server.analysis_results.get())
    item = mbapi.PopulationItem(
        name="a_population_name",
        analysis_type_id=analysis_result.analysis_type_id,
        category="a_population_category",
        condition=mbapi.FilterGroupConditionItem(
            operator="AND",
            conditions=[
                mbapi.FilterAccountConditionItem(
                    account_selections=[
                        mbapi.FilterAccountSelectionItem(
                            use_account_id=False, code="1000", name="Assets"
                        )
                    ],
                    field="account_hierarchy_codes",
                ),
                mbapi.FilterDateValueSpecificValueConditionItem(
                    field="effective_date", value=date(2000, 1, 1)
                ),
            ],
        ),
        analysis_id=analysis_result.analysis_id,
    )
    ```

    Attributes:
        id (str): The unique object identifier.
        name (str): The name of the population.
        analysis_id (str): The ID of the parent analysis.
        analysis_type_id: (str): Identifies the analysis type associated with this
            population.
        category (str): The category of the population.
        condition (FilterGroupConditionItem): The filter condition used to determine
            which entries are included in the population.
        base_population_id (str): The ID of the population the current population is
            based on.
        cloned_from (str): Identifies the population the current population was cloned
            from.
        derived_from_engagement (bool): Indicates whether the analysis population was
            derived from an engagement.
        derived_from_library (bool): Indicates that the engagement population was
            derived from a library.
        description (str): A description of the population.
        disabled (bool):
        disabled_for_analysis_ids (list[str]): Lists the analysis IDs where the
            engagement population is disabled.
        display_currency_code (str): The ISO 4217 three-digit currency code that
            determines how currency values are formatted. Defaults to `USD` if not
            specified.
        display_locale (str): The ISO 639 locale identifier used to format display
            values. Defaults to `en-us` if not specified.
        engagement_id (str): The ID of the parent engagement.
        legacy_filter_format (bool): If `true`, this population uses a legacy filter
            format that cannot be represented in the current condition format.
        library_id (str): The ID of the parent library.
        promoted_from_analysis_id (str): Identifies the analysis from which the
            engagement population was promoted.
        reason_for_change (str): The reason for the latest change made to the
            population.
    """

    condition: FilterGroupConditionItem | None = Field().merge_field_infos(
        ApiPopulationTagRead.model_fields["condition"]
    )

    model_config = ConfigDict(
        extra="allow",
        validate_assignment=True,
        validate_default=True,
        validate_return=True,
    )
    _a = model_validator(mode="after")(_warning_if_extra_fields)
    _b = field_validator("*")(_convert_userinfo_to_useritem)

    def _get_post_json(
        self, out_class: type[PopulationItemCreate | PopulationItemUpdate]
    ) -> dict[str, Any]:
        in_class_dict = self.model_dump()
        out_class_object = out_class.model_validate(in_class_dict)
        return out_class_object.model_dump(
            mode="json", by_alias=True, exclude_none=True
        )

    @property
    def create_json(self) -> dict[str, Any]:
        return self._get_post_json(out_class=PopulationItemCreate)

    @property
    def update_json(self) -> dict[str, Any]:
        return self._get_post_json(out_class=PopulationItemUpdate)
