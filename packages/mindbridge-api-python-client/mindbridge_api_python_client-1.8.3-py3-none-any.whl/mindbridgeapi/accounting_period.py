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
from mindbridgeapi.generated_pydantic_model.model import (
    ApiAccountingPeriodRead,
    Frequency,
)


class AccountingPeriod(ApiAccountingPeriodRead):
    fiscal_start_month: Annotated[
        int,
        Field(
            alias=ApiAccountingPeriodRead.model_fields["fiscal_start_month"].alias,
            description=ApiAccountingPeriodRead.model_fields[
                "fiscal_start_month"
            ].description,
        ),
    ] = 1
    fiscal_start_day: Annotated[
        int,
        Field(
            alias=ApiAccountingPeriodRead.model_fields["fiscal_start_day"].alias,
            description=ApiAccountingPeriodRead.model_fields[
                "fiscal_start_day"
            ].description,
        ),
    ] = 1
    frequency: Annotated[
        Frequency,
        Field(
            description=ApiAccountingPeriodRead.model_fields[
                "fiscal_start_day"
            ].description
        ),
    ] = Frequency.ANNUAL

    model_config = ConfigDict(
        extra="allow",
        validate_assignment=True,
        validate_default=True,
        validate_return=True,
    )
    _ = model_validator(mode="after")(_warning_if_extra_fields)
