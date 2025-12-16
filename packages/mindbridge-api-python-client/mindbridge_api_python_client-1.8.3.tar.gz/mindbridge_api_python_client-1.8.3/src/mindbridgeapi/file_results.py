#
#  Copyright MindBridge Analytics Inc. all rights reserved.
#
#  This material is confidential and may not be copied, distributed,
#  reversed engineered, decompiled or otherwise disseminated without
#  the prior written consent of MindBridge Analytics Inc.
#

from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING, Any
from mindbridgeapi.base_set import BaseSet
from mindbridgeapi.exceptions import ItemNotFoundError
from mindbridgeapi.file_result_item import FileResultItem

if TYPE_CHECKING:
    from collections.abc import Generator
    from pathlib import Path


@dataclass
class FileResults(BaseSet):
    @cached_property
    def base_url(self) -> str:
        return f"{self.server.base_url}/file-results"

    def get_by_id(self, id: str) -> FileResultItem:
        url = f"{self.base_url}/{id}"
        resp_dict = super()._get_by_id(url=url)
        return FileResultItem.model_validate(resp_dict)

    def get(
        self, json: dict[str, Any] | None = None
    ) -> "Generator[FileResultItem, None, None]":
        if json is None:
            json = {}

        url = f"{self.base_url}/query"
        for resp_dict in super()._get(url=url, json=json):
            yield FileResultItem.model_validate(resp_dict)

    def export(self, file_result: FileResultItem, output_file_path: "Path") -> "Path":
        if file_result.id is None:
            raise ItemNotFoundError

        url = f"{self.base_url}/{file_result.id}/export"

        return super()._download(url=url, output_path=output_file_path)
