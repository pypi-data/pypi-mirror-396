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
from mindbridgeapi.api_token_item import ApiTokenItem
from mindbridgeapi.base_set import BaseSet
from mindbridgeapi.exceptions import ItemAlreadyExistsError, ItemNotFoundError

if TYPE_CHECKING:
    from collections.abc import Generator


@dataclass
class ApiTokens(BaseSet):
    """Use to interact with API tokens.

    Typical usage of these functions would be accessed from the server, for example:
    ```py
    from datetime import datetime, timedelta, timezone
    import mindbridgeapi as mbapi

    server = mbapi.Server(url="subdomain.mindbridge.ai", token="my_secret_token")
    token = mbapi.ApiTokenItem(
        name="My Token Name",
        expiry=datetime.now(tz=timezone.utc) + timedelta(hours=1),
        permissions=[mbapi.ApiTokenPermission.API_ORGANIZATIONS_READ],
    )
    token = server.api_tokens.create(token)
    print(f"Created {token.name!r}")
    secret_token_str = token.token
    ```
    """

    @cached_property
    def base_url(self) -> str:
        return f"{self.server.base_url}/api-tokens"

    def create(self, item: ApiTokenItem) -> ApiTokenItem:
        """Creates a new API token on the server.

        Args:
            item (ApiTokenItem): The API token item to create.

        Returns:
            (ApiTokenItem): The created API token item.

        Raises:
            ItemAlreadyExistsError: If the item already has an ID.
        """
        item = ApiTokenItem.model_validate(item)

        if item.id:
            raise ItemAlreadyExistsError(item.id)

        resp_dict = super()._create(url=self.base_url, json=item.create_json)
        return ApiTokenItem.model_validate(resp_dict)

    def delete(self, item: ApiTokenItem) -> None:
        """Deletes an API token from the server.

        Args:
            item (ApiTokenItem): The API token item to delete.

        Raises:
            ItemNotFoundError: If the item does not have an ID.
        """
        item = ApiTokenItem.model_validate(item)

        if not item.id:
            raise ItemNotFoundError

        super()._delete(url=f"{self.base_url}/{item.id}")

    def get_current(self) -> ApiTokenItem:
        """Retrieves the current API token from the server.

        Returns:
            (ApiTokenItem): The current API token item.
        """
        resp_dict = super()._get_by_id(url=f"{self.base_url}/current")

        return ApiTokenItem.model_validate(resp_dict)

    def get(
        self, json: dict[str, Any] | None = None
    ) -> "Generator[ApiTokenItem, None, None]":
        """Retrieves API tokens from the server based on the provided query parameters.

        Args:
            json (Optional[dict[str, Any]]): Query parameters for filtering API tokens.

        Yields:
            (ApiTokenItem): A generator of API token items.
        """
        if json is None:
            json = {}

        for resp_dict in super()._get(url=f"{self.base_url}/query", json=json):
            yield ApiTokenItem.model_validate(resp_dict)

    def get_by_id(self, id: str) -> ApiTokenItem:
        """Retrieves an API token by its ID from the server.

        Args:
            id (str): The ID of the API token to retrieve.

        Returns:
            (ApiTokenItem): The API token item with the specified ID.
        """
        resp_dict = super()._get_by_id(url=f"{self.base_url}/{id}")

        return ApiTokenItem.model_validate(resp_dict)

    def update(self, item: ApiTokenItem) -> ApiTokenItem:
        """Updates an existing API token on the server.

        Args:
            item (ApiTokenItem): The API token item to update.

        Returns:
            (ApiTokenItem): The updated API token item.

        Raises:
            ItemNotFoundError: If the item does not have an ID.
        """
        item = ApiTokenItem.model_validate(item)

        if not item.id:
            raise ItemNotFoundError

        resp_dict = super()._update(
            url=f"{self.base_url}/{item.id}", json=item.update_json
        )

        return ApiTokenItem.model_validate(resp_dict)
