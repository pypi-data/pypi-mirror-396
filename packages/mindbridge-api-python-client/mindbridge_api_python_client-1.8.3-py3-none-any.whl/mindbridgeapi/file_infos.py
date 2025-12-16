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
from mindbridgeapi.file_info_item import FileInfoItem

if TYPE_CHECKING:
    from collections.abc import Generator


@dataclass
class FileInfos(BaseSet):
    """Use to interact with File Infos.

    Typical usage of these functions would be accessed from the server, for example:
    ```py
    import os
    import mindbridgeapi as mbapi

    server = mbapi.Server(
        url=os.environ["MINDBRIDGE_API_TEST_URL"],
        token=os.environ["MINDBRIDGE_API_TEST_TOKEN"],
    )
    file_manager_item = server.file_manager.get_by_id("real_file_object_id_here")
    file_info = server.file_infos.get_by_id(file_manager_item.file_info_id)
    print(f"{file_manager_item.filename!r} has the first line: {file_info.first_line}")
    ```
    """

    @cached_property
    def base_url(self) -> str:
        return f"{self.server.base_url}/file-infos"

    def get_by_id(self, id: str) -> FileInfoItem:
        """Retrieves a File Info by its ID from the server.

        Args:
            id (str): The ID of the File Info to retrieve.

        Returns:
            (FileInfoItem): The File Info item with the specified ID.
        """
        resp_dict = super()._get_by_id(url=f"{self.base_url}/{id}")
        return FileInfoItem.model_validate(resp_dict)

    def get(
        self, json: dict[str, Any] | None = None
    ) -> "Generator[FileInfoItem, None, None]":
        """Retrieves File Infos from the server based on the provided query parameters.

        Args:
            json (dict[str, Any]): Optional query parameters for filtering File Infos.

        Yields:
            (FileInfoItem): A generator of File Infos items.
        """
        if json is None:
            json = {}

        for resp_dict in super()._get(url=f"{self.base_url}/query", json=json):
            yield FileInfoItem.model_validate(resp_dict)
