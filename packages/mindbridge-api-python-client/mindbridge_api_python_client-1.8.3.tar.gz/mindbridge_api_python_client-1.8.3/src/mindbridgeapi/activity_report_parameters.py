#
#  Copyright MindBridge Analytics Inc. all rights reserved.
#
#  This material is confidential and may not be copied, distributed,
#  reversed engineered, decompiled or otherwise disseminated without
#  the prior written consent of MindBridge Analytics Inc.
#

from typing import Any
from pydantic import ConfigDict, model_validator
from mindbridgeapi.common_validators import _warning_if_extra_fields
from mindbridgeapi.generated_pydantic_model.model import (
    Category as _ActivityReportCategory,
    RunActivityReportRequestCreate,
)

ActivityReportCategory = (
    _ActivityReportCategory  # Match the type of ActivityReportParameters.categories
)


class ActivityReportParameters(RunActivityReportRequestCreate):
    """Parameters to use with `server.admin_reports.run_activity_report`.

    ```py
    from datetime import datetime, timezone
    import mindbridgeapi as mbapi

    activity_report_parameters = mbapi.ActivityReportParameters(
        start=datetime.now(tz=timezone.utc),
        end=datetime.max.replace(tzinfo=timezone.utc),
    )
    ```

    Attributes:
        start (datetime): The first date in the reporting timeframe.
        end (datetime): The last date in the reporting timeframe.
        user_ids (Optional[list[str]]): The users to include in the report. If empty,
            all users will be included.
        categories (Optional[list[ActivityReportCategory]]): The categories to include
            in the report. If empty, all categories will be included.
        only_completed_analyses (Optional[bool]): Restrict entries to analysis complete
            events.
    """

    model_config = ConfigDict(
        extra="allow",
        validate_assignment=True,
        validate_default=True,
        validate_return=True,
    )
    _ = model_validator(mode="after")(_warning_if_extra_fields)

    @property
    def create_json(self) -> dict[str, Any]:
        in_class_dict = self.model_dump()
        out_class_object = RunActivityReportRequestCreate.model_validate(in_class_dict)
        return out_class_object.model_dump(
            mode="json", by_alias=True, exclude_none=True
        )
