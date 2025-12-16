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
from mindbridgeapi.analysis_types import AnalysisTypes
from mindbridgeapi.base_set import BaseSet
from mindbridgeapi.exceptions import ItemAlreadyExistsError, ItemNotFoundError
from mindbridgeapi.library_item import LibraryItem

if TYPE_CHECKING:
    from collections.abc import Generator


@dataclass
class Libraries(BaseSet):
    """Use to interact with Libraries.

    Typical usage of these functions would be accessed from the server, for example:
    ```py
    import os
    import mindbridgeapi as mbapi

    server = mbapi.Server(
        url=os.environ["MINDBRIDGE_API_TEST_URL"],
        token=os.environ["MINDBRIDGE_API_TEST_TOKEN"],
    )
    account_grouping = next(
        x
        for x in server.account_groupings.get()
        if x.system and x.name.get("en") == "MAC v.2"
    )
    library = mbapi.LibraryItem(
        name="My Library Name", account_grouping_id=account_grouping.id
    )
    library = server.libraries.create(library)
    print(f"Created {library.name}")
    ```
    """

    @cached_property
    def base_url(self) -> str:
        return f"{self.server.base_url}/libraries"

    def create(self, library_item: LibraryItem) -> LibraryItem:
        """Creates a new Library on the server.

        Args:
            library_item (LibraryItem): The Library to create.

        Returns:
            (LibraryItem): The created Library.

        Raises:
            ItemAlreadyExistsError: If the library_item already has an ID.
        """
        library_item = LibraryItem.model_validate(library_item)
        if library_item.id:
            raise ItemAlreadyExistsError(library_item.id)

        resp_dict = super()._create(url=self.base_url, json=library_item.create_json)
        library_item = LibraryItem.model_validate(resp_dict)
        self.restart_analysis_types(library_item)
        return library_item

    def delete(self, library_item: LibraryItem) -> None:
        """Deletes an existing Library.

        Args:
            library_item (LibraryItem): The Library to delete.

        Raises:
            ItemNotFoundError: If the library_item does not have an ID.
        """
        library_item = LibraryItem.model_validate(library_item)

        if not library_item.id:
            raise ItemNotFoundError

        super()._delete(url=f"{self.base_url}/{library_item.id}")

    def get(
        self, json: dict[str, Any] | None = None
    ) -> "Generator[LibraryItem, None, None]":
        """Retrieves Libraries.

        Retrieves Libraries from the server based on the optionally provided query
            parameters.

        Args:
            json (dict[str, Any]): The query parameters.

        Yields:
            (LibraryItem): A generator of Libraries.
        """
        if json is None:
            json = {}

        for resp_dict in super()._get(url=f"{self.base_url}/query", json=json):
            library_item = LibraryItem.model_validate(resp_dict)
            self.restart_analysis_types(library_item)
            yield library_item

    def get_by_id(self, id: str) -> LibraryItem:
        """Retrieves a Library by its ID.

        Args:
            id (str): The ID of the Library to retrieve.

        Returns:
            (LibraryItem): The retrieved Library.
        """
        resp_dict = super()._get_by_id(url=f"{self.base_url}/{id}")
        library_item = LibraryItem.model_validate(resp_dict)
        self.restart_analysis_types(library_item)
        return library_item

    def update(self, library_item: LibraryItem) -> LibraryItem:
        """Updates an existing Library.

        Args:
            library_item (LibraryItem): The Library to update.

        Returns:
            (LibraryItem): The updated Library.

        Raises:
            ItemNotFoundError: If the library_item does not have an ID.
        """
        library_item = LibraryItem.model_validate(library_item)

        if not library_item.id:
            raise ItemNotFoundError

        resp_dict = super()._update(
            url=f"{self.base_url}/{library_item.id}", json=library_item.update_json
        )

        library_item = LibraryItem.model_validate(resp_dict)
        self.restart_analysis_types(library_item)
        return library_item

    def restart_analysis_types(self, library_item: LibraryItem) -> None:
        """Restarts the analysis_types generator.

        Args:
            library_item (LibraryItem): The Library to update.

        Raises:
            ItemNotFoundError: If the library_item does not have an ID.
        """
        library_item = LibraryItem.model_validate(library_item)

        if not library_item.id:
            raise ItemNotFoundError

        if library_item.analysis_type_ids:
            library_item.analysis_types = AnalysisTypes(server=self.server).get(
                json={"id": {"$in": library_item.analysis_type_ids}}
            )
