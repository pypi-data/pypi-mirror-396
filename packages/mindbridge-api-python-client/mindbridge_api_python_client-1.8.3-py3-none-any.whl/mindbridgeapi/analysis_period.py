#
#  Copyright MindBridge Analytics Inc. all rights reserved.
#
#  This material is confidential and may not be copied, distributed,
#  reversed engineered, decompiled or otherwise disseminated without
#  the prior written consent of MindBridge Analytics Inc.
#

from datetime import date, datetime, timezone
from typing import Annotated
from pydantic import ConfigDict, Field, model_validator
from mindbridgeapi.common_validators import _warning_if_extra_fields
from mindbridgeapi.generated_pydantic_model.model import ApiAnalysisPeriodRead


class AnalysisPeriod(ApiAnalysisPeriodRead):
    start_date: Annotated[
        date,
        Field(
            alias=ApiAnalysisPeriodRead.model_fields["start_date"].alias,
            description=ApiAnalysisPeriodRead.model_fields["start_date"].description,
        ),
    ] = date(datetime.now(tz=timezone.utc).astimezone().year - 1, 1, 1)
    end_date: Annotated[
        date,
        Field(
            alias=ApiAnalysisPeriodRead.model_fields["end_date"].alias,
            description=ApiAnalysisPeriodRead.model_fields["end_date"].description,
        ),
    ] = date(datetime.now(tz=timezone.utc).astimezone().year - 1, 12, 31)

    model_config = ConfigDict(
        extra="allow",
        validate_assignment=True,
        validate_default=True,
        validate_return=True,
    )
    _ = model_validator(mode="after")(_warning_if_extra_fields)

    def __lt__(self, other: object) -> bool:
        """Sort as current then prior period 1, 2, 3, 4 (newest to oldest).

        Returns:
            self > other
        """
        if not isinstance(other, AnalysisPeriod):
            return NotImplemented

        return (self.start_date > other.end_date) or (
            (self.end_date == other.end_date) and (self.start_date > other.start_date)
        )
