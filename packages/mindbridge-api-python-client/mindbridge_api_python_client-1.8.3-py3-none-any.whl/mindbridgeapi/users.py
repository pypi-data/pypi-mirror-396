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
from mindbridgeapi.exceptions import ItemAlreadyExistsError, ItemNotFoundError
from mindbridgeapi.user_item import UserItem

if TYPE_CHECKING:
    from collections.abc import Generator


@dataclass
class Users(BaseSet):
    """Use to interact with Users.

    Typical usage of these functions would be accessed from the server, for example:
    ```py
    import mindbridgeapi as mbapi

    server = mbapi.Server(url="subdomain.mindbridge.ai", token="my_secret_token")
    user = mbapi.UserItem(email="person@example.com", role=mbapi.UserRole.ROLE_USER)
    user = server.users.create(user)
    print(f"Created a user with email: {user.email!r}")
    ```
    """

    @cached_property
    def base_url(self) -> str:
        return f"{self.server.base_url}/users"

    def create(self, item: UserItem) -> UserItem:
        """Create a new user on the server.

        Args:
            item (UserItem): The user item to create.

        Returns:
            (UserItem): The created user item.
        """
        item = UserItem.model_validate(item)

        if item.id:
            raise ItemAlreadyExistsError(item.id)

        resp_dict = super()._create(url=self.base_url, json=item.create_json)
        return UserItem.model_validate(resp_dict)

    def delete(self, item: UserItem) -> None:
        """Delete a user from the server.

        Args:
            item (UserItem): The user item to delete.

        Raises:
            ItemNotFoundError: If the user item does not have an ID.
        """
        item = UserItem.model_validate(item)

        if not item.id:
            raise ItemNotFoundError

        super()._delete(url=f"{self.base_url}/{item.id}")

    def get_current(self) -> UserItem:
        """Retrieve the currently authenticated user.

        Returns:
            (UserItem): The current user item.
        """
        resp_dict = super()._get_by_id(url=f"{self.base_url}/current")
        return UserItem.model_validate(resp_dict)

    def get(
        self, json: dict[str, Any] | None = None
    ) -> "Generator[UserItem, None, None]":
        """Retrieve a list of users based on query parameters.

        Args:
            json (dict[str, Any]): Query parameters for filtering users.

        Yields:
            (UserItem): A generator of user items.
        """
        if json is None:
            json = {}

        for resp_dict in super()._get(url=f"{self.base_url}/query", json=json):
            yield UserItem.model_validate(resp_dict)

    def get_by_id(self, id: str) -> UserItem:
        """Retrieve a user by their ID.

        Args:
            id (str): The ID of the user.

        Returns:
            (UserItem): The user item with the specified ID.
        """
        resp_dict = super()._get_by_id(url=f"{self.base_url}/{id}")
        return UserItem.model_validate(resp_dict)

    def resend_activation_link(self, item: UserItem) -> UserItem:
        """Resend the activation link for a user.

        Args:
            item (UserItem): The user item to resend the activation link for.

        Raises:
            ItemNotFoundError: If the user item does not have an ID.

        Returns:
            (UserItem): The user item after resending the activation link.
        """
        item = UserItem.model_validate(item)

        if not item.id:
            raise ItemNotFoundError

        resp_dict = super()._create(
            url=f"{self.base_url}/{item.id}/resend-activation-link", json={}
        )
        return UserItem.model_validate(resp_dict)

    def update(self, item: UserItem) -> UserItem:
        """Update an existing user on the server.

        Args:
            item (UserItem): The user item to update.

        Raises:
            ItemNotFoundError: If the user item does not have an ID.

        Returns:
            (UserItem): The updated user item.
        """
        item = UserItem.model_validate(item)

        if not item.id:
            raise ItemNotFoundError

        resp_dict = super()._update(
            url=f"{self.base_url}/{item.id}", json=item.update_json
        )
        return UserItem.model_validate(resp_dict)
