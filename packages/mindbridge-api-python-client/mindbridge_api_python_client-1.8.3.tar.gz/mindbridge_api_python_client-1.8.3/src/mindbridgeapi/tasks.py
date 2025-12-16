#
#  Copyright MindBridge Analytics Inc. all rights reserved.
#
#  This material is confidential and may not be copied, distributed,
#  reversed engineered, decompiled or otherwise disseminated without
#  the prior written consent of MindBridge Analytics Inc.
#
from dataclasses import dataclass
from functools import cached_property
import logging
from typing import TYPE_CHECKING, Any
import warnings
from mindbridgeapi.base_set import BaseSet
from mindbridgeapi.common_validators import _convert_json_query
from mindbridgeapi.exceptions import ItemAlreadyExistsError, ItemNotFoundError
from mindbridgeapi.generated_pydantic_model.model import ApiTaskCommentCreate
from mindbridgeapi.task_item import TaskItem

if TYPE_CHECKING:
    from collections.abc import Generator

logger = logging.getLogger(__name__)


@dataclass
class Tasks(BaseSet):
    @cached_property
    def base_url(self) -> str:
        return f"{self.server.base_url}/tasks"

    def create(self, item: TaskItem, max_wait_minutes: int = -99) -> TaskItem:
        """Creates a new task.

        Creates a new task on the server retrying if needed

        Args:
            item (TaskItem): The task to be created
            max_wait_minutes (int): Deprecated: Will be 30 minutes

        Returns:
            TaskItem: The successfully created task

        Raises:
            ItemAlreadyExistsError: If the item had an id
        """
        if max_wait_minutes != -99:  # noqa: PLR2004
            warnings.warn(
                f"max_wait_minutes was provided to create as {max_wait_minutes}. This "
                "will not be referenced as now the max_wait_minutes will be 30 for "
                "this request",
                category=DeprecationWarning,
                stacklevel=2,
            )

        del max_wait_minutes

        item = TaskItem.model_validate(item)

        if item.id:
            raise ItemAlreadyExistsError(item.id)

        resp_dict = super()._create(
            url=self.base_url, json=item.create_json, try_again_if_locked=True
        )
        item = TaskItem.model_validate(resp_dict)
        self.restart_task_histories(item)
        return item

    def add_comment(self, id: str, text: str) -> TaskItem:
        url = f"{self.base_url}/{id}/add-comment"
        create_json = ApiTaskCommentCreate(comment_text=text).model_dump(by_alias=True)
        resp_dict = super()._create(url=url, json=create_json)
        task = TaskItem.model_validate(resp_dict)
        self.restart_task_histories(task)
        return task

    def get_by_id(self, id: str) -> TaskItem:
        url = f"{self.base_url}/{id}"
        resp_dict = super()._get_by_id(url=url)
        task = TaskItem.model_validate(resp_dict)
        self.restart_task_histories(task)
        return task

    def update(self, item: TaskItem) -> TaskItem:
        if getattr(item, "id", None) is None:
            raise ItemNotFoundError

        url = f"{self.base_url}/{item.id}"
        resp_dict = super()._update(url=url, json=item.update_json)

        task = TaskItem.model_validate(resp_dict)
        self.restart_task_histories(task)
        return task

    def get(
        self, json: dict[str, Any] | None = None
    ) -> "Generator[TaskItem, None, None]":
        mb_query_dict = _convert_json_query(json, required_key="analysisId")

        url = f"{self.base_url}/query"
        for resp_dict in super()._get(url=url, json=mb_query_dict):
            task = TaskItem.model_validate(resp_dict)
            self.restart_task_histories(task)
            yield task

    def delete(self, item: TaskItem) -> None:
        if getattr(item, "id", None) is None:
            raise ItemNotFoundError

        url = f"{self.base_url}/{item.id}"
        super()._delete(url=url)

    def restart_task_histories(self, task: TaskItem) -> None:
        if getattr(task, "id", None) is None:
            raise ItemNotFoundError

        task.task_histories = self.server.task_histories.get(
            json={"taskId": {"$eq": task.id}}
        )
