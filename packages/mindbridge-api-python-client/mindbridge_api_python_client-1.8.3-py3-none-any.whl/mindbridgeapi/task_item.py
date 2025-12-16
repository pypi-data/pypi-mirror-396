#
#  Copyright MindBridge Analytics Inc. all rights reserved.
#
#  This material is confidential and may not be copied, distributed,
#  reversed engineered, decompiled or otherwise disseminated without
#  the prior written consent of MindBridge Analytics Inc.
#

from collections.abc import Generator
from typing import Annotated, Any
from pydantic import ConfigDict, Field, field_validator, model_validator
from mindbridgeapi.common_validators import (
    _convert_userinfo_to_useritem,
    _warning_if_extra_fields,
)
from mindbridgeapi.generated_pydantic_model.model import (
    ApiTaskCreate,
    ApiTaskRead,
    ApiTaskUpdate,
    Status6 as _TaskStatus,
    Type67 as _TaskType,
)
from mindbridgeapi.task_history_item import TaskHistoryItem

TaskStatus = _TaskStatus  # Match the type of TaskItem.status
TaskType = _TaskType  # Match the type of TaskItem.type
_out_class = type[ApiTaskCreate | ApiTaskUpdate]


def _empty_task_histories() -> Generator[TaskHistoryItem, None, None]:
    """Empty generator function.

    This returns an empty generator function, it's use is to ensure task_histories is
    not None for the TaskItem class

    Yields:
        TaskHistoryItem: Will never yield anything
    """
    yield from ()


class TaskItem(ApiTaskRead):
    task_histories: Annotated[
        Generator[TaskHistoryItem, None, None], Field(exclude=True)
    ] = _empty_task_histories()

    model_config = ConfigDict(
        extra="allow",
        validate_assignment=True,
        validate_default=True,
        validate_return=True,
    )
    _a = model_validator(mode="after")(_warning_if_extra_fields)
    _b = field_validator("*")(_convert_userinfo_to_useritem)

    def _get_post_json(self, out_class: _out_class) -> dict[str, Any]:
        in_class_dict = self.model_dump()
        out_class_object = out_class.model_validate(in_class_dict)
        return out_class_object.model_dump(
            mode="json", by_alias=True, exclude_none=True
        )

    @property
    def create_json(self) -> dict[str, Any]:
        return self._get_post_json(out_class=ApiTaskCreate)

    @property
    def update_json(self) -> dict[str, Any]:
        return self._get_post_json(out_class=ApiTaskUpdate)
