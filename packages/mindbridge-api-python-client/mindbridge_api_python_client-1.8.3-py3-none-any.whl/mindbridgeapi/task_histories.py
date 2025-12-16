#
#  Copyright MindBridge Analytics Inc. all rights reserved.
#
#  This material is confidential and may not be copied, distributed,
#  reversed engineered, decompiled or otherwise disseminated without
#  the prior written consent of MindBridge Analytics Inc.
#

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any
from mindbridgeapi.base_set import BaseSet
from mindbridgeapi.common_validators import _convert_json_query
from mindbridgeapi.task_history_item import TaskHistoryItem

if TYPE_CHECKING:
    from collections.abc import Generator


@dataclass
class TaskHistories(BaseSet):
    base_url: str = field(init=False)

    def __post_init__(self) -> None:
        self.base_url = f"{self.server.base_url}/task-histories"

    def get_by_id(self, id: str) -> TaskHistoryItem:
        url = f"{self.base_url}/{id}"
        resp_dict = super()._get_by_id(url=url)

        return TaskHistoryItem.model_validate(resp_dict)

    def get(
        self, json: dict[str, Any] | None = None
    ) -> "Generator[TaskHistoryItem, None, None]":
        mb_query_dict = _convert_json_query(json, required_key="taskId")

        url = f"{self.base_url}/query"
        for resp_dict in super()._get(url=url, json=mb_query_dict):
            yield TaskHistoryItem.model_validate(resp_dict)
