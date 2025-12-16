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
from pathlib import Path
from typing import TYPE_CHECKING, Any, Union
import warnings
from mindbridgeapi.async_result_item import AsyncResultItem, AsyncResultType
from mindbridgeapi.base_set import BaseSet
from mindbridgeapi.exceptions import (
    ItemAlreadyExistsError,
    ItemError,
    ItemNotFoundError,
    ParameterError,
    UnexpectedServerError,
)
from mindbridgeapi.file_manager_item import FileManagerItem, FileManagerType
from mindbridgeapi.generated_pydantic_model.model import (
    ApiFileMergeRequestCreate,
    ApiJsonTableRead,
    CreateApiFileManagerFileFromJsonTableRequestCreate,
)

if TYPE_CHECKING:
    from collections.abc import Generator
    from os import PathLike
    from mindbridgeapi.chunked_file_item import ChunkedFileItem

logger = logging.getLogger(__name__)


@dataclass
class FileManager(BaseSet):
    @cached_property
    def base_url(self) -> str:
        return f"{self.server.base_url}/file-manager"

    def mkdir(self, item: FileManagerItem) -> FileManagerItem:
        if getattr(item, "id", None) is not None and item.id is not None:
            raise ItemAlreadyExistsError(item.id)

        url = self.base_url
        resp_dict = super()._create(url=url, json=item.create_json)

        return FileManagerItem.model_validate(resp_dict)

    def get_by_id(self, id: str) -> FileManagerItem:
        url = f"{self.base_url}/{id}"
        resp_dict = super()._get_by_id(url=url)

        return FileManagerItem.model_validate(resp_dict)

    def update(self, item: FileManagerItem) -> FileManagerItem:
        if getattr(item, "id", None) is None:
            raise ItemNotFoundError

        url = f"{self.base_url}/{item.id}"
        resp_dict = super()._update(url=url, json=item.update_json)

        return FileManagerItem.model_validate(resp_dict)

    def get(
        self, json: dict[str, Any] | None = None
    ) -> "Generator[FileManagerItem, None, None]":
        if json is None:
            json = {}

        url = f"{self.base_url}/query"

        for resp_dict in super()._get(url=url, json=json):
            yield FileManagerItem.model_validate(resp_dict)

    def delete(self, item: FileManagerItem) -> None:
        if getattr(item, "id", None) is None:
            raise ItemNotFoundError

        url = f"{self.base_url}/{item.id}"
        super()._delete(url=url)

    def upload(
        self, input_item: FileManagerItem, input_file: Union[str, "PathLike[Any]"]
    ) -> FileManagerItem:
        input_file_path = Path(input_file)

        if not input_file_path.is_file():
            raise ParameterError(
                parameter_name="input_file_path",
                details=f"{input_file_path} is not a file.",
            )

        if not input_item.name:
            input_item.name = input_file_path.stem

        if not input_item.extension and input_file_path.suffix:
            input_item.extension = input_file_path.suffix[1:]

        chunk_size = 50 * 2**20  # 50 MB
        file_size = input_file_path.stat().st_size
        if file_size <= 0:
            raise ParameterError(
                parameter_name="input_file_path",
                details=f"File size of {file_size} is too small",
            )

        number_of_parts = file_size // chunk_size
        if file_size % chunk_size > 0:
            number_of_parts += 1

        file_name = input_item.filename

        logger.info(
            "Preparing to upload a file with %i chunks, using a size of %i bytes",
            number_of_parts,
            chunk_size,
        )

        if number_of_parts <= 1:
            logger.info(
                'Using the "Create File Manager File From Multipart File" method'
            )
            url = f"{self.base_url}/import"

            with input_file_path.open("rb") as open_file:
                upload_bytes = open_file.read()

            files: dict[str, Any] = {
                "fileManagerFile": (None, input_item.create_body, "application/json"),
                "file": (file_name, upload_bytes),
            }

            logger.info(
                "upload with fileManagerFile data as %s", input_item.create_body
            )

            resp_dict = self._upload(url=url, files=files)

            return FileManagerItem.model_validate(resp_dict)

        logger.info('Using the "Chunked Files" method')
        chunked_file = self.server.chunked_files.upload(input_file_path)

        return self.import_from_chunked(chunked_file, input_item)

    def download(
        self, input_item: FileManagerItem, output_file: Union[str, "PathLike[Any]"]
    ) -> Path:
        if getattr(input_item, "id", None) is None:
            raise ItemNotFoundError

        if FileManagerType(input_item.type) == FileManagerType.DIRECTORY:
            msg = f"Unexpected value of {input_item.type} for type."
            raise ItemError(msg)

        output_file_path = Path(output_file)

        output_file_path = output_file_path.expanduser()

        if output_file_path.is_dir():
            output_file_path /= input_item.filename
        elif output_file_path.exists():
            logger.info("%s already exists, will be overwritten", output_file_path)
        elif output_file_path.parent.is_dir():
            logger.info("%s will be created", output_file_path)
        else:
            raise ParameterError(
                parameter_name="output_file",
                details=f"{output_file_path} is not a valid download location",
            )

        url = f"{self.base_url}/{input_item.id}/export"

        return super()._download(url=url, output_path=output_file_path)

    def import_from_chunked(
        self, chunked_file_item: "ChunkedFileItem", file_manager_item: FileManagerItem
    ) -> FileManagerItem:
        if getattr(chunked_file_item, "id", None) is None:
            raise ItemNotFoundError

        url = f"{self.base_url}/import-from-chunked/{chunked_file_item.id}"

        resp_dict = super()._create(url=url, json=file_manager_item.create_json)

        return FileManagerItem.model_validate(resp_dict)

    def merge(
        self,
        file_manager_item: FileManagerItem,
        file_column_mappings: dict[str, list[int]],
    ) -> FileManagerItem:
        """Merges multiple files into a single file using specified column mappings.

        Args:
            file_manager_item (FileManagerItem): The file manager item representing the
                output file.
            file_column_mappings (dict[str, list[int]]): A dictionary mapping file IDs
                to column indices.

        Returns:
            FileManagerItem: The resulting merged file manager item.

        Raises:
            ItemAlreadyExistsError: If the file manager item already has an ID.
            ItemError: If the engagement ID is not provided or invalid.
            ParameterError: If the column mappings are invalid or insufficient for
                merging.
            UnexpectedServerError: If the server returns an unexpected result.
        """
        file_manager_item = FileManagerItem.model_validate(file_manager_item)

        if file_manager_item.id:
            raise ItemAlreadyExistsError(file_manager_item.id)

        if not file_manager_item.engagement_id:
            msg = "engagement_id must be provided"
            raise ItemError(msg)

        merge_request_item = ApiFileMergeRequestCreate(
            engagement_id=file_manager_item.engagement_id,
            file_column_mappings=file_column_mappings,
            output_file_name=file_manager_item.filename,
            parent_file_manager_entity_id=file_manager_item.parent_file_manager_entity_id,
        )

        if (
            not merge_request_item.file_column_mappings
            or len(merge_request_item.file_column_mappings) <= 1
        ):
            raise ParameterError(
                parameter_name="file_column_mappings",
                details="To merge there must be 2 or more files",
            )

        col_len = -1
        for columns in merge_request_item.file_column_mappings.values():
            if col_len == -1:
                col_len = len(columns)

            if len(columns) == 0 or col_len != len(columns):
                raise ParameterError(
                    parameter_name="file_column_mappings",
                    details=(
                        "All files to merge must have the same number of selected "
                        "columns and more than 0"
                    ),
                )

        resp_dict = super()._create(
            url=f"{self.base_url}/transform/merge",
            json=merge_request_item.model_dump(
                mode="json", by_alias=True, exclude_none=True
            ),
        )
        async_result = AsyncResultItem.model_validate(resp_dict)
        if not async_result.entity_id:
            msg = "No Entity ID for async result."
            raise UnexpectedServerError(msg)

        if async_result.type != AsyncResultType.DATA_TRANSFORMATION_JOB:
            msg = f"AsyncResultType was {async_result.type}."
            raise UnexpectedServerError(msg)

        return self.get_by_id(async_result.entity_id)

    def import_from_json_table(
        self, json_table_item: ApiJsonTableRead, file_manager_item: FileManagerItem
    ) -> FileManagerItem:
        """Create a new file manager file from a JSON table.

        Args:
            json_table_item (ApiJsonTableRead): The JSON table item to create the file
                from.
            file_manager_item (FileManagerItem): File Manager Item to be created.

        Returns:
            FileManagerItem: The created file manager file.
        """
        json_table_item = ApiJsonTableRead.model_validate(json_table_item)

        if not json_table_item.id:
            raise ParameterError(
                parameter_name="json_table_item", details="Must have an id."
            )

        file_manager_item = FileManagerItem.model_validate(file_manager_item)

        if not file_manager_item.engagement_id:
            raise ParameterError(
                parameter_name="file_manager_item",
                details="Must have an engagement_id.",
            )

        if not file_manager_item.name:
            raise ParameterError(
                parameter_name="file_manager_item", details="Must have an name."
            )

        if file_manager_item.extension and file_manager_item.extension != "csv":
            warnings.warn(
                (
                    "All imports from a JSON table are csv, so the csv extension will "
                    f" be used instead of {file_manager_item.extension}"
                ),
                stacklevel=2,
            )

        request_obj = CreateApiFileManagerFileFromJsonTableRequestCreate(
            engagement_id=file_manager_item.engagement_id,
            json_table_id=json_table_item.id,
            name=file_manager_item.name,
            parent_file_manager_entity_id=file_manager_item.parent_file_manager_entity_id,
        )

        resp_dict = super()._create(
            url=f"{self.base_url}/import-from-json-table",
            json=request_obj.model_dump(mode="json", by_alias=True, exclude_none=True),
        )
        return FileManagerItem.model_validate(resp_dict)
