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
from mindbridgeapi.generated_pydantic_model.model import RunAdminReportRequestCreate


class RowUsageReportParameters(RunAdminReportRequestCreate):
    """Parameters to use with `server.admin_reports.test_run_row_usage_report`.

    ```py
    from datetime import datetime, timezone
    import mindbridgeapi as mbapi

    row_usage_report_parameters = mbapi.RowUsageReportParameters(
        start=datetime.now(tz=timezone.utc),
        end=datetime.max.replace(tzinfo=timezone.utc),
    )
    ```

    Attributes:
        start (datetime): The first date in the reporting timeframe.
        end (datetime): The last date in the reporting timeframe.
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
        out_class_object = RunAdminReportRequestCreate.model_validate(in_class_dict)
        return out_class_object.model_dump(
            mode="json", by_alias=True, exclude_none=True
        )
