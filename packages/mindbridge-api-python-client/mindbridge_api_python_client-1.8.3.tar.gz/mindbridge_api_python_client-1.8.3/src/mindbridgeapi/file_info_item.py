from mindbridgeapi.generated_pydantic_model.model import (
    ApiTabularFileInfoRead,
    Type7 as _FileInfoType,
)

# Match the type of ApiTabularFileInfoRead.type:
FileInfoType = _FileInfoType


class FileInfoItem(ApiTabularFileInfoRead):
    """Represents a specific MindBridge File Info.

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

    Attributes:
        id (str): The unique object identifier.
        name (str): The name of the underlying file or table.
        type (FileInfoType): The type of file info entity.
        format_detected (bool): When `true` a known grouped format was detected.
        format (Format): The grouped format that was detected.
        column_data (list[ApiColumnDataRead]): A list of column metadata entities,
            describing each column.
        delimiter (str): The delimiter character used to separate cells. Only populated
            when the underlying file is a CSV file.
        first_line (str): The first line of the table.
        header_row_index (int): The row number of the first detected header.
        last_non_blank_row_index (int): The row number of the last row that isn't blank.
        row_content_snippets (list[list[str]]): A list of sample rows from the
            underlying file.
        table_metadata (ApiTableMetadataRead): A collection of metadata describing the
            table as a whole.
    """
