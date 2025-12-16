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
    ApiRiskRangesCreate,
    ApiRiskRangesRead,
    ApiRiskRangesUpdate,
)


class RiskRangesItem(ApiRiskRangesRead):
    """Represents a specific MindBridge Risk Ranges.

    ```py
    import os
    import uuid
    import mindbridgeapi as mbapi

    server = mbapi.Server(
        url=os.environ["MINDBRIDGE_API_TEST_URL"],
        token=os.environ["MINDBRIDGE_API_TEST_TOKEN"],
    )
    library = next(x for x in server.libraries.get() if not x.system)
    item = mbapi.RiskRangesItem(
        name=f"risk_range_{uuid.uuid4().hex}",
        library_id=library.id,
        analysis_type_id=library.analysis_type_ids[0],
        low=mbapi.RiskRangeBounds(low_threshold=0, high_threshold=50_00),
        high=mbapi.RiskRangeBounds(low_threshold=50_01, high_threshold=100_00),
    )
    ```

    Attributes:
        id (str): The unique object identifier.
        analysis_type_id (str): Identifies the analysis type associated with this risk
            range.
        name (str): The name of the risk range.
        engagement_id (Optional[str]): Identifies the engagement associated with this
            risk range.
        library_id (Optional[str]): Identifies the library associated with this
            risk range.
        description (Optional[str]): The description of the risk range.
        low (Optional[RiskRangeBounds]): The low range bounds.
        medium (Optional[RiskRangeBounds]): The medium range bounds.
        high (Optional[RiskRangeBounds]): The high range bounds.
    """

    model_config = ConfigDict(
        extra="allow",
        validate_assignment=True,
        validate_default=True,
        validate_return=True,
    )
    _ = model_validator(mode="after")(_warning_if_extra_fields)

    def _get_post_json(
        self, out_class: type[ApiRiskRangesCreate | ApiRiskRangesUpdate]
    ) -> dict[str, Any]:
        in_class_dict = self.model_dump()
        out_class_object = out_class.model_validate(in_class_dict)
        return out_class_object.model_dump(
            mode="json", by_alias=True, exclude_none=True
        )

    @property
    def create_json(self) -> dict[str, Any]:
        return self._get_post_json(out_class=ApiRiskRangesCreate)

    @property
    def update_json(self) -> dict[str, Any]:
        return self._get_post_json(out_class=ApiRiskRangesUpdate)
