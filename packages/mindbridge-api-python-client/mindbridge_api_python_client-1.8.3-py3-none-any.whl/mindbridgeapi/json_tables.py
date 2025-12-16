#
#  Copyright MindBridge Analytics Inc. all rights reserved.
#
#  This material is confidential and may not be copied, distributed,
#  reversed engineered, decompiled or otherwise disseminated without
#  the prior written consent of MindBridge Analytics Inc.
#

from dataclasses import dataclass
from functools import cached_property
from typing import Annotated
from annotated_types import MinLen
from pydantic import RootModel
from mindbridgeapi.base_set import BaseSet
from mindbridgeapi.exceptions import ItemNotFoundError
from mindbridgeapi.generated_pydantic_model.model import ApiJsonTableRead

_JSONAppendData = RootModel[
    Annotated[
        list[Annotated[dict[str, int | float | bool | str], MinLen(1)]], MinLen(1)
    ]
]


@dataclass
class JSONTables(BaseSet):
    """Use to interact with JSON Tables.

    Typical usage of these functions would be accessed from the server, for example:
    ```py
    import mindbridgeapi as mbapi

    server = mbapi.Server(url="subdomain.mindbridge.ai", token="my_secret_token")

    engagement = server.engagements.get_by_id("abc")

    json_table = server.json_tables.create()
    json_table = server.json_tables.append(
        json_table_item=json_table,
        data=[{"col1": "value1", "col2": 123}, {"col1": "value2", "col2": 456}],
    )
    file_manager_item = server.file_manager.import_from_json_table(
        json_table_item=json_table,
        file_manager_item=mbapi.FileManagerItem(
            engagement_id=engagement.id, name="My File"
        ),
    )
    print(
        f"Created {file_manager_item.filename!r} in the {engagement.name!r} File "
        "manager."
    )
    ```
    """

    @cached_property
    def base_url(self) -> str:
        return f"{self.server.base_url}/json-tables"

    def append(
        self, json_table_item: ApiJsonTableRead, data: _JSONAppendData
    ) -> ApiJsonTableRead:
        """Append data to a JSON table.

        Args:
            json_table_item (ApiJsonTableRead): The JSON table item to append data to.
            data (_JSONAppendData): The data to append, must be a list of dictionaries.

        Returns:
            (ApiJsonTableRead): The updated JSON table item after appending the data.

        Raises:
            ItemNotFoundError: If the JSON table item does not exist.
        """
        json_table_item = ApiJsonTableRead.model_validate(json_table_item)

        if not json_table_item.id:
            raise ItemNotFoundError

        data = _JSONAppendData.model_validate(data)

        resp_dict = super()._create(
            url=f"{self.base_url}/{json_table_item.id}/append",
            json=data.model_dump(mode="json", exclude_none=True),
        )
        return ApiJsonTableRead.model_validate(resp_dict)

    def create(self) -> ApiJsonTableRead:
        """Create a new JSON table.

        Returns:
            (ApiJsonTableRead): The created JSON table item.
        """
        resp_dict = super()._create(url=self.base_url, json=None)
        return ApiJsonTableRead.model_validate(resp_dict)

    def get_by_id(self, id: str) -> ApiJsonTableRead:
        """Get a JSON table by its ID.

        Args:
            id (str): The ID of the JSON table.

        Returns:
            (ApiJsonTableRead): The JSON table item with the specified ID.
        """
        resp_dict = super()._get_by_id(url=f"{self.base_url}/{id}")
        return ApiJsonTableRead.model_validate(resp_dict)
