#
#  Copyright MindBridge Analytics Inc. all rights reserved.
#
#  This material is confidential and may not be copied, distributed,
#  reversed engineered, decompiled or otherwise disseminated without
#  the prior written consent of MindBridge Analytics Inc.
#

import logging
from pydantic import ConfigDict, field_validator, model_validator
from mindbridgeapi.common_validators import (
    _convert_userinfo_to_useritem,
    _warning_if_extra_fields,
)
from mindbridgeapi.exceptions import ItemError, ItemNotFoundError, ValidationError
from mindbridgeapi.generated_pydantic_model.model import (
    ApiAsyncResult,
    Status3 as _AsyncResultStatus,
    Type3 as _AsyncResultType,
)

logger = logging.getLogger(__name__)

AsyncResultStatus = _AsyncResultStatus  # Match the type of AsyncResultItem.status
AsyncResultType = _AsyncResultType  # Match the type of AsyncResultItem.type


class AsyncResultItem(ApiAsyncResult):
    model_config = ConfigDict(
        extra="allow",
        validate_assignment=True,
        validate_default=True,
        validate_return=True,
    )
    _a = model_validator(mode="after")(_warning_if_extra_fields)
    _b = field_validator("*")(_convert_userinfo_to_useritem)

    def _check_if_completed(self) -> bool:
        """Checks if the AsyncResultItem is completed.

        Returns True if COMPLETE, False if IN_PROGRESS and raises and error otherwise.

        Returns:
            bool: True if COMPLETE, False if IN_PROGRESS

        Raises:
            ValidationError: If the async_result resulted in an error state
        """
        async_result_str = (
            f"Async Result {self.id} for"
            f" {self.entity_type} {self.entity_id} resulted in"
            f" {self.status}"
        )
        logger.info(async_result_str)

        if self.status == AsyncResultStatus.IN_PROGRESS:
            return False

        if self.status == AsyncResultStatus.COMPLETE:
            return True

        # Must be AsyncResultStatus.ERROR
        msg = f"{async_result_str} with message {self.error}."
        raise ValidationError(msg)

    def _get_file_result_id(self, expected_type: AsyncResultType) -> str:
        if self.type != expected_type:
            msg = f"{self.type=}."
            raise ItemError(msg)

        if self.status != AsyncResultStatus.COMPLETE:
            msg = f"{self.status=}."
            raise ItemError(msg)

        if self.entity_id is None:
            raise ItemNotFoundError

        return self.entity_id
