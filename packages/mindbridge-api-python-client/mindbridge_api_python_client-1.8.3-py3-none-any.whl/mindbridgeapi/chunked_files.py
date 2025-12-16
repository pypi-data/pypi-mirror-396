#
#  Copyright MindBridge Analytics Inc. all rights reserved.
#
#  This material is confidential and may not be copied, distributed,
#  reversed engineered, decompiled or otherwise disseminated without
#  the prior written consent of MindBridge Analytics Inc.
#

from dataclasses import dataclass
from functools import cached_property, partial
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Union
from mindbridgeapi.base_set import BaseSet
from mindbridgeapi.chunked_file_item import ChunkedFileItem
from mindbridgeapi.chunked_file_part_item import ChunkedFilePartItem
from mindbridgeapi.exceptions import (
    ItemAlreadyExistsError,
    ItemNotFoundError,
    ParameterError,
)

if TYPE_CHECKING:
    from collections.abc import Generator
    from os import PathLike

logger = logging.getLogger(__name__)


@dataclass
class ChunkedFiles(BaseSet):
    @cached_property
    def base_url(self) -> str:
        return f"{self.server.base_url}/chunked-files"

    def get_by_id(self, id: str) -> ChunkedFileItem:
        url = f"{self.base_url}/{id}"
        resp_dict = super()._get_by_id(url=url)

        return ChunkedFileItem.model_validate(resp_dict)

    def get(
        self, json: dict[str, Any] | None = None
    ) -> "Generator[ChunkedFileItem, None, None]":
        if json is None:
            json = {}

        url = f"{self.base_url}/query"
        for resp_dict in super()._get(url=url, json=json):
            yield ChunkedFileItem.model_validate(resp_dict)

    def send_chunk(
        self,
        chunked_file_item: ChunkedFileItem,
        chunked_file_part_item: ChunkedFilePartItem,
        data: bytes,
    ) -> None:
        if getattr(chunked_file_item, "id", None) is None:
            raise ItemNotFoundError

        url = f"{self.base_url}/{chunked_file_item.id}/part"
        files = {
            "chunkedFilePart": (
                None,
                chunked_file_part_item.create_body,
                "application/json",
            ),
            "fileChunk": (chunked_file_item.name, data),
        }

        super()._upload(url=url, files=files)

    def upload(self, input_file: Union[str, "PathLike[Any]"]) -> ChunkedFileItem:
        input_file_path = Path(input_file)

        if not input_file_path.is_file():
            raise ParameterError(
                parameter_name="input_file", details=f"{input_file_path} is not a file."
            )

        chunk_size = 50 * 2**20  # 50 MB
        file_size = input_file_path.stat().st_size
        if file_size <= 0:
            raise ParameterError(
                parameter_name="input_file",
                details=(
                    f"{input_file_path.name} has a file size of {file_size} which is "
                    "too small."
                ),
            )

        number_of_parts = file_size // chunk_size
        if file_size % chunk_size > 0:
            number_of_parts += 1

        max_allowed_number_of_parts = 1000
        if number_of_parts > max_allowed_number_of_parts:
            raise ParameterError(
                parameter_name="input_file",
                details=(
                    f"{input_file_path.name} has a file size of {file_size} which is "
                    "too big."
                ),
            )

        chunked_file = ChunkedFileItem(size=file_size, name=input_file_path.name)
        chunked_file = self.create(chunked_file)

        with input_file_path.open("rb") as file:
            offset = 0
            for i, data in enumerate(
                iter(partial(file.read, chunk_size), b""), start=1
            ):
                size = len(data)

                chunked_file_part = ChunkedFilePartItem(size=size, offset=offset)
                self.server.chunked_files.send_chunk(
                    chunked_file, chunked_file_part, data
                )
                logger.info("Sent chunk %i of %i", i, number_of_parts)

                offset += size

        return chunked_file

    def create(self, item: ChunkedFileItem) -> ChunkedFileItem:
        if getattr(item, "id", None) is not None and item.id is not None:
            raise ItemAlreadyExistsError(item.id)

        url = self.base_url
        resp_dict = super()._create(url=url, json=item.create_json)

        return ChunkedFileItem.model_validate(resp_dict)

    def delete(self, item: ChunkedFileItem) -> None:
        """Delete a chunked file from the server.

        Args:
            item (ChunkedFileItem): The chunked file to delete.

        Raises:
            ItemNotFoundError: If the item does not have an ID.
        """
        item = ChunkedFileItem.model_validate(item)

        if not item.id:
            raise ItemNotFoundError

        super()._delete(url=f"{self.base_url}/{item.id}")
