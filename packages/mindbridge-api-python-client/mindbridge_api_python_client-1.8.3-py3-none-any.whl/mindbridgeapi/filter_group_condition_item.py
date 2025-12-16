#
#  Copyright MindBridge Analytics Inc. all rights reserved.
#
#  This material is confidential and may not be copied, distributed,
#  reversed engineered, decompiled or otherwise disseminated without
#  the prior written consent of MindBridge Analytics Inc.
#

from typing import Annotated, Literal, Union
from pydantic import ConfigDict, Field, RootModel, model_validator
from mindbridgeapi.common_validators import _warning_if_extra_fields
from mindbridgeapi.generated_pydantic_model.model import (
    ApiFilterAccountCondition,
    ApiFilterComplexMonetaryFlowCondition,
    ApiFilterControlPointCondition,
    ApiFilterDateRangeCondition,
    ApiFilterDateValueCondition,
    ApiFilterGroupConditionRead,
    ApiFilterMaterialityOptionCondition,
    ApiFilterMaterialityValueCondition,
    ApiFilterMonetaryValueRangeCondition,
    ApiFilterMonetaryValueValueCondition,
    ApiFilterNumericalValueRangeCondition,
    ApiFilterNumericalValueValueCondition,
    ApiFilterPopulationsCondition,
    ApiFilterRiskScoreHMLCondition,
    ApiFilterRiskScorePercentRangeCondition,
    ApiFilterRiskScorePercentUnscoredCondition,
    ApiFilterRiskScorePercentValueCondition,
    ApiFilterSimpleMonetaryFlowCondition,
    ApiFilterSpecificMonetaryFlowRangeCondition,
    ApiFilterSpecificMonetaryFlowValueCondition,
    ApiFilterStringArrayCondition,
    ApiFilterStringCondition,
    ApiFilterTypeaheadEntryCondition,
)


class FilterAccountConditionItem(ApiFilterAccountCondition):
    type: Literal["ACCOUNT_NODE_ARRAY"] = Field().merge_field_infos(
        ApiFilterAccountCondition.model_fields["type"]
    )


class FilterControlPointConditionItem(ApiFilterControlPointCondition):
    type: Literal["CONTROL_POINT"] = Field().merge_field_infos(
        ApiFilterControlPointCondition.model_fields["type"]
    )


class FilterPopulationsConditionItem(ApiFilterPopulationsCondition):
    type: Literal["POPULATIONS"] = Field().merge_field_infos(
        ApiFilterPopulationsCondition.model_fields["type"]
    )


class FilterStringArrayConditionItem(ApiFilterStringArrayCondition):
    type: Literal["STRING_ARRAY"] = Field().merge_field_infos(
        ApiFilterStringArrayCondition.model_fields["type"]
    )


class FilterStringConditionItem(ApiFilterStringCondition):
    type: Literal["STRING"] = Field().merge_field_infos(
        ApiFilterStringCondition.model_fields["type"]
    )


class FilterTypeaheadEntryConditionItem(ApiFilterTypeaheadEntryCondition):
    type: Literal["TYPEAHEAD_ENTRY"] = Field().merge_field_infos(
        ApiFilterTypeaheadEntryCondition.model_fields["type"]
    )


class FilterRiskScoreHMLConditionItem(ApiFilterRiskScoreHMLCondition):
    type: Literal["RISK_SCORE"] = Field().merge_field_infos(
        ApiFilterRiskScoreHMLCondition.model_fields["type"]
    )
    risk_score_type: Literal["HML"] = Field().merge_field_infos(
        ApiFilterRiskScoreHMLCondition.model_fields["risk_score_type"]
    )


class FilterRiskScorePercentRangeConditionCustomRangeItem(
    ApiFilterRiskScorePercentRangeCondition
):
    type: Literal["RISK_SCORE"] = Field().merge_field_infos(
        ApiFilterRiskScorePercentRangeCondition.model_fields["type"]
    )
    risk_score_type: Literal["PERCENT"] = Field().merge_field_infos(
        ApiFilterRiskScorePercentRangeCondition.model_fields["risk_score_type"]
    )
    risk_score_percent_type: Literal["CUSTOM_RANGE"] = Field().merge_field_infos(
        ApiFilterRiskScorePercentRangeCondition.model_fields["risk_score_percent_type"],
        default="CUSTOM_RANGE",
    )  # type: ignore[assignment]


class FilterRiskScorePercentRangeConditionBetweenItem(
    ApiFilterRiskScorePercentRangeCondition
):
    type: Literal["RISK_SCORE"] = Field().merge_field_infos(
        ApiFilterRiskScorePercentRangeCondition.model_fields["type"]
    )
    risk_score_type: Literal["PERCENT"] = Field().merge_field_infos(
        ApiFilterRiskScorePercentRangeCondition.model_fields["risk_score_type"]
    )
    risk_score_percent_type: Literal["BETWEEN"] = Field().merge_field_infos(
        ApiFilterRiskScorePercentRangeCondition.model_fields["risk_score_percent_type"],
        default="BETWEEN",
    )  # type: ignore[assignment]


class FilterRiskScorePercentUnscoredConditionItem(
    ApiFilterRiskScorePercentUnscoredCondition
):
    type: Literal["RISK_SCORE"] = Field().merge_field_infos(
        ApiFilterRiskScorePercentUnscoredCondition.model_fields["type"]
    )
    risk_score_type: Literal["PERCENT"] = Field().merge_field_infos(
        ApiFilterRiskScorePercentUnscoredCondition.model_fields["risk_score_type"]
    )
    risk_score_percent_type: Literal["UNSCORED"] = Field().merge_field_infos(
        ApiFilterRiskScorePercentUnscoredCondition.model_fields[
            "risk_score_percent_type"
        ]
    )


class FilterRiskScorePercentValueConditionMoreThanItem(
    ApiFilterRiskScorePercentValueCondition
):
    type: Literal["RISK_SCORE"] = Field().merge_field_infos(
        ApiFilterRiskScorePercentValueCondition.model_fields["type"]
    )
    risk_score_type: Literal["PERCENT"] = Field().merge_field_infos(
        ApiFilterRiskScorePercentValueCondition.model_fields["risk_score_type"]
    )
    risk_score_percent_type: Literal["MORE_THAN"] = Field().merge_field_infos(
        ApiFilterRiskScorePercentValueCondition.model_fields["risk_score_percent_type"],
        default="MORE_THAN",
    )  # type: ignore[assignment]


class FilterRiskScorePercentValueConditionLessThanItem(
    ApiFilterRiskScorePercentValueCondition
):
    type: Literal["RISK_SCORE"] = Field().merge_field_infos(
        ApiFilterRiskScorePercentValueCondition.model_fields["type"]
    )
    risk_score_type: Literal["PERCENT"] = Field().merge_field_infos(
        ApiFilterRiskScorePercentValueCondition.model_fields["risk_score_type"]
    )
    risk_score_percent_type: Literal["LESS_THAN"] = Field().merge_field_infos(
        ApiFilterRiskScorePercentValueCondition.model_fields["risk_score_percent_type"],
        default="LESS_THAN",
    )  # type: ignore[assignment]


FilterRiskScorePercentConditionItem = Annotated[
    FilterRiskScorePercentRangeConditionCustomRangeItem
    | FilterRiskScorePercentRangeConditionBetweenItem
    | FilterRiskScorePercentUnscoredConditionItem
    | FilterRiskScorePercentValueConditionMoreThanItem
    | FilterRiskScorePercentValueConditionLessThanItem,
    Field(discriminator="risk_score_percent_type"),
]

FilterRiskScoreConditionItem = Annotated[
    FilterRiskScoreHMLConditionItem | FilterRiskScorePercentConditionItem,
    Field(discriminator="risk_score_type"),
]


class FilterComplexMonetaryFlowConditionItem(ApiFilterComplexMonetaryFlowCondition):
    type: Literal["MONETARY_FLOW"] = Field().merge_field_infos(
        ApiFilterComplexMonetaryFlowCondition.model_fields["type"]
    )
    monetary_flow_type: Literal["COMPLEX_FLOW"] = Field().merge_field_infos(
        ApiFilterComplexMonetaryFlowCondition.model_fields["monetary_flow_type"]
    )


class FilterSimpleMonetaryFlowConditionItem(ApiFilterSimpleMonetaryFlowCondition):
    type: Literal["MONETARY_FLOW"] = Field().merge_field_infos(
        ApiFilterSimpleMonetaryFlowCondition.model_fields["type"]
    )
    monetary_flow_type: Literal["SIMPLE_FLOW"] = Field().merge_field_infos(
        ApiFilterSimpleMonetaryFlowCondition.model_fields["monetary_flow_type"]
    )


class FilterSpecificMonetaryFlowRangeConditionItem(
    ApiFilterSpecificMonetaryFlowRangeCondition
):
    type: Literal["MONETARY_FLOW"] = Field().merge_field_infos(
        ApiFilterSpecificMonetaryFlowRangeCondition.model_fields["type"]
    )
    monetary_flow_type: Literal["SPECIFIC_FLOW"] = Field().merge_field_infos(
        ApiFilterSpecificMonetaryFlowRangeCondition.model_fields["monetary_flow_type"]
    )
    specific_monetary_flow_type: Literal["BETWEEN"] = Field().merge_field_infos(
        ApiFilterSpecificMonetaryFlowRangeCondition.model_fields[
            "specific_monetary_flow_type"
        ]
    )


class FilterSpecificMonetaryFlowValueConditionSpecificValueItem(
    ApiFilterSpecificMonetaryFlowValueCondition
):
    type: Literal["MONETARY_FLOW"] = Field().merge_field_infos(
        ApiFilterSpecificMonetaryFlowValueCondition.model_fields["type"]
    )
    monetary_flow_type: Literal["SPECIFIC_FLOW"] = Field().merge_field_infos(
        ApiFilterSpecificMonetaryFlowValueCondition.model_fields["monetary_flow_type"]
    )
    specific_monetary_flow_type: Literal["SPECIFIC_VALUE"] = Field().merge_field_infos(
        ApiFilterSpecificMonetaryFlowValueCondition.model_fields[
            "specific_monetary_flow_type"
        ],
        default="SPECIFIC_VALUE",
    )  # type: ignore[assignment]


class FilterSpecificMonetaryFlowValueConditionMoreThanItem(
    ApiFilterSpecificMonetaryFlowValueCondition
):
    type: Literal["MONETARY_FLOW"] = Field().merge_field_infos(
        ApiFilterSpecificMonetaryFlowValueCondition.model_fields["type"]
    )
    monetary_flow_type: Literal["SPECIFIC_FLOW"] = Field().merge_field_infos(
        ApiFilterSpecificMonetaryFlowValueCondition.model_fields["monetary_flow_type"]
    )
    specific_monetary_flow_type: Literal["MORE_THAN"] = Field().merge_field_infos(
        ApiFilterSpecificMonetaryFlowValueCondition.model_fields[
            "specific_monetary_flow_type"
        ],
        default="MORE_THAN",
    )  # type: ignore[assignment]


FilterSpecificMonetaryFlowConditionItem = Annotated[
    FilterSpecificMonetaryFlowRangeConditionItem
    | FilterSpecificMonetaryFlowValueConditionSpecificValueItem
    | FilterSpecificMonetaryFlowValueConditionMoreThanItem,
    Field(discriminator="specific_monetary_flow_type"),
]

FilterMonetaryFlowConditionItem = Annotated[
    FilterComplexMonetaryFlowConditionItem
    | FilterSimpleMonetaryFlowConditionItem
    | FilterSpecificMonetaryFlowConditionItem,
    Field(discriminator="monetary_flow_type"),
]


class FilterMonetaryValueRangeConditionItem(ApiFilterMonetaryValueRangeCondition):
    type: Literal["MONEY"] = Field().merge_field_infos(
        ApiFilterMonetaryValueRangeCondition.model_fields["type"]
    )
    monetary_value_type: Literal["BETWEEN"] = Field().merge_field_infos(
        ApiFilterMonetaryValueRangeCondition.model_fields["monetary_value_type"]
    )


class FilterMonetaryValueValueConditionMoreThanItem(
    ApiFilterMonetaryValueValueCondition
):
    type: Literal["MONEY"] = Field().merge_field_infos(
        ApiFilterMonetaryValueValueCondition.model_fields["type"]
    )
    monetary_value_type: Literal["MORE_THAN"] = Field().merge_field_infos(
        ApiFilterMonetaryValueValueCondition.model_fields["monetary_value_type"],
        default="MORE_THAN",
    )  # type: ignore[assignment]


class FilterMonetaryValueValueConditionSpecificValueItem(
    ApiFilterMonetaryValueValueCondition
):
    type: Literal["MONEY"] = Field().merge_field_infos(
        ApiFilterMonetaryValueValueCondition.model_fields["type"]
    )
    monetary_value_type: Literal["SPECIFIC_VALUE"] = Field().merge_field_infos(
        ApiFilterMonetaryValueValueCondition.model_fields["monetary_value_type"],
        default="SPECIFIC_VALUE",
    )  # type: ignore[assignment]


class FilterMonetaryValueValueConditionLessThanItem(
    ApiFilterMonetaryValueValueCondition
):
    type: Literal["MONEY"] = Field().merge_field_infos(
        ApiFilterMonetaryValueValueCondition.model_fields["type"]
    )
    monetary_value_type: Literal["LESS_THAN"] = Field().merge_field_infos(
        ApiFilterMonetaryValueValueCondition.model_fields["monetary_value_type"],
        default="LESS_THAN",
    )  # type: ignore[assignment]


FilterMonetaryValueConditionItem = Annotated[
    FilterMonetaryValueRangeConditionItem
    | FilterMonetaryValueValueConditionMoreThanItem
    | FilterMonetaryValueValueConditionSpecificValueItem
    | FilterMonetaryValueValueConditionLessThanItem,
    Field(discriminator="monetary_value_type"),
]


class FilterMaterialityOptionConditionAboveItem(ApiFilterMaterialityOptionCondition):
    type: Literal["MATERIALITY"] = Field().merge_field_infos(
        ApiFilterMaterialityOptionCondition.model_fields["type"]
    )
    materiality_option: Literal["ABOVE"] = Field().merge_field_infos(
        ApiFilterMaterialityOptionCondition.model_fields["materiality_option"],
        default="ABOVE",
    )  # type: ignore[assignment]


class FilterMaterialityOptionConditionBelowItem(ApiFilterMaterialityOptionCondition):
    type: Literal["MATERIALITY"] = Field().merge_field_infos(
        ApiFilterMaterialityOptionCondition.model_fields["type"]
    )
    materiality_option: Literal["BELOW"] = Field().merge_field_infos(
        ApiFilterMaterialityOptionCondition.model_fields["materiality_option"],
        default="BELOW",
    )  # type: ignore[assignment]


class FilterMaterialityValueConditionItem(ApiFilterMaterialityValueCondition):
    type: Literal["MATERIALITY"] = Field().merge_field_infos(
        ApiFilterMaterialityValueCondition.model_fields["type"]
    )
    materiality_option: Literal["PERCENTAGE"] = Field().merge_field_infos(
        ApiFilterMaterialityValueCondition.model_fields["materiality_option"]
    )


FilterMaterialityConditionItem = Annotated[
    FilterMaterialityOptionConditionAboveItem
    | FilterMaterialityOptionConditionBelowItem
    | FilterMaterialityValueConditionItem,
    Field(discriminator="materiality_option"),
]


class FilterNumericalValueRangeConditionItem(ApiFilterNumericalValueRangeCondition):
    type: Literal["NUMERICAL"] = Field().merge_field_infos(
        ApiFilterNumericalValueRangeCondition.model_fields["type"]
    )
    numerical_value_type: Literal["BETWEEN"] = Field().merge_field_infos(
        ApiFilterNumericalValueRangeCondition.model_fields["numerical_value_type"]
    )


class FilterNumericalValueValueConditionMoreThanItem(
    ApiFilterNumericalValueValueCondition
):
    type: Literal["NUMERICAL"] = Field().merge_field_infos(
        ApiFilterNumericalValueValueCondition.model_fields["type"]
    )
    numerical_value_type: Literal["MORE_THAN"] = Field().merge_field_infos(
        ApiFilterNumericalValueValueCondition.model_fields["numerical_value_type"],
        default="MORE_THAN",
    )  # type: ignore[assignment]


class FilterNumericalValueValueConditionSpecificValueItem(
    ApiFilterNumericalValueValueCondition
):
    type: Literal["NUMERICAL"] = Field().merge_field_infos(
        ApiFilterNumericalValueValueCondition.model_fields["type"]
    )
    numerical_value_type: Literal["SPECIFIC_VALUE"] = Field().merge_field_infos(
        ApiFilterNumericalValueValueCondition.model_fields["numerical_value_type"],
        default="SPECIFIC_VALUE",
    )  # type: ignore[assignment]


class FilterNumericalValueValueConditionLessThanItem(
    ApiFilterNumericalValueValueCondition
):
    type: Literal["NUMERICAL"] = Field().merge_field_infos(
        ApiFilterNumericalValueValueCondition.model_fields["type"]
    )
    numerical_value_type: Literal["LESS_THAN"] = Field().merge_field_infos(
        ApiFilterNumericalValueValueCondition.model_fields["numerical_value_type"],
        default="LESS_THAN",
    )  # type: ignore[assignment]


FilterNumericalValueConditionItem = Annotated[
    FilterNumericalValueRangeConditionItem
    | FilterNumericalValueValueConditionMoreThanItem
    | FilterNumericalValueValueConditionSpecificValueItem
    | FilterNumericalValueValueConditionLessThanItem,
    Field(discriminator="numerical_value_type"),
]


class FilterDateRangeConditionItem(ApiFilterDateRangeCondition):
    type: Literal["DATE"] = Field().merge_field_infos(
        ApiFilterDateRangeCondition.model_fields["type"]
    )
    date_type: Literal["BETWEEN"] = Field().merge_field_infos(
        ApiFilterDateRangeCondition.model_fields["date_type"]
    )


class FilterDateValueAfterConditionItem(ApiFilterDateValueCondition):
    type: Literal["DATE"] = Field().merge_field_infos(
        ApiFilterDateValueCondition.model_fields["type"]
    )
    date_type: Literal["AFTER"] = Field().merge_field_infos(
        ApiFilterDateValueCondition.model_fields["date_type"], default="AFTER"
    )  # type: ignore[assignment]


class FilterDateValueBeforeConditionItem(ApiFilterDateValueCondition):
    type: Literal["DATE"] = Field().merge_field_infos(
        ApiFilterDateValueCondition.model_fields["type"]
    )
    date_type: Literal["BEFORE"] = Field().merge_field_infos(
        ApiFilterDateValueCondition.model_fields["date_type"], default="BEFORE"
    )  # type: ignore[assignment]


class FilterDateValueSpecificValueConditionItem(ApiFilterDateValueCondition):
    type: Literal["DATE"] = Field().merge_field_infos(
        ApiFilterDateValueCondition.model_fields["type"]
    )
    date_type: Literal["SPECIFIC_VALUE"] = Field().merge_field_infos(
        ApiFilterDateValueCondition.model_fields["date_type"], default="SPECIFIC_VALUE"
    )  # type: ignore[assignment]


FilterDateConditionItem = Annotated[
    FilterDateRangeConditionItem
    | FilterDateValueAfterConditionItem
    | FilterDateValueBeforeConditionItem
    | FilterDateValueSpecificValueConditionItem,
    Field(discriminator="date_type"),
]


class FilterCondition(
    RootModel[
        Union[
            "FilterGroupConditionItem",
            FilterStringConditionItem,
            FilterStringArrayConditionItem,
            FilterControlPointConditionItem,
            FilterAccountConditionItem,
            FilterTypeaheadEntryConditionItem,
            FilterPopulationsConditionItem,
            FilterRiskScoreConditionItem,
            FilterMonetaryFlowConditionItem,
            FilterMonetaryValueConditionItem,
            FilterMaterialityConditionItem,
            FilterNumericalValueConditionItem,
            FilterDateConditionItem,
        ]
    ]
):
    """Used internally when updating a Filter Group Condition Item."""

    model_config = ConfigDict(populate_by_name=True)
    root: Annotated[
        Union[
            "FilterGroupConditionItem",
            FilterStringConditionItem,
            FilterStringArrayConditionItem,
            FilterControlPointConditionItem,
            FilterAccountConditionItem,
            FilterTypeaheadEntryConditionItem,
            FilterPopulationsConditionItem,
            FilterRiskScoreConditionItem,
            FilterMonetaryFlowConditionItem,
            FilterMonetaryValueConditionItem,
            FilterMaterialityConditionItem,
            FilterNumericalValueConditionItem,
            FilterDateConditionItem,
        ],
        Field(discriminator="type", title="Filter Condition"),
    ]


class FilterGroupConditionItem(ApiFilterGroupConditionRead):
    conditions: list[FilterCondition] = Field().merge_field_infos(
        ApiFilterGroupConditionRead.model_fields["conditions"]
    )  # type: ignore[assignment]
    type: Literal["GROUP"] = Field().merge_field_infos(
        ApiFilterGroupConditionRead.model_fields["type"]
    )

    model_config = ConfigDict(
        extra="allow",
        validate_assignment=True,
        validate_default=True,
        validate_return=True,
    )
    _ = model_validator(mode="after")(_warning_if_extra_fields)
