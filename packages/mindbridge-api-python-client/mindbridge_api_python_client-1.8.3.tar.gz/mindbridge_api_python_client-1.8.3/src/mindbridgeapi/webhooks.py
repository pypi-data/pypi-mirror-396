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
from mindbridgeapi.webhook_item import WebhookItem

if TYPE_CHECKING:
    from collections.abc import Generator


@dataclass
class Webhooks(BaseSet):
    """Use to interact with Webhooks.

    Typical usage of these functions would be accessed from the server, for example:
    ```py
    import os
    import mindbridgeapi as mbapi

    server = mbapi.Server(
        url=os.environ["MINDBRIDGE_API_TEST_URL"],
        token=os.environ["MINDBRIDGE_API_TEST_TOKEN"],
    )
    user = next(server.users.get({"role": mbapi.UserRole.ROLE_ADMIN}))
    webhook = mbapi.WebhookItem(
        url=webhook_url,
        events=[mbapi.WebhookEvent.ENGAGEMENT_CREATED],
        status=mbapi.WebhookStatus.ACTIVE,
        name="webhook_952679e5683948dcb2892af7e75d9b21",
        technical_contact_id=user.id,
    )
    webhook = server.webhooks.create(webhook)
    print(f"Created {webhook.name}")
    ```
    """

    @cached_property
    def base_url(self) -> str:
        return f"{self.server.base_url}/webhooks"

    def create(self, item: WebhookItem) -> WebhookItem:
        """Create a new webhook on the server.

        Args:
            item (WebhookItem): The webhook to create.

        Returns:
            (WebhookItem): The created webhook.
        """
        item = WebhookItem.model_validate(item)

        if item.id:
            raise ItemAlreadyExistsError(item.id)

        resp_dict = super()._create(url=self.base_url, json=item.create_json)
        return WebhookItem.model_validate(resp_dict)

    def delete(self, item: WebhookItem) -> None:
        """Delete a webhook from the server.

        Args:
            item (WebhookItem): The webhook to delete.

        Raises:
            ItemNotFoundError: If the webhook item does not have an ID.
        """
        item = WebhookItem.model_validate(item)

        if not item.id:
            raise ItemNotFoundError

        super()._delete(url=f"{self.base_url}/{item.id}")

    def get(
        self, json: dict[str, Any] | None = None
    ) -> "Generator[WebhookItem, None, None]":
        """Retrieve a list of webhooks based on query parameters.

        Args:
            json (dict[str, Any]): Optional query parameters for filtering webhooks.

        Yields:
            (WebhookItem): A generator of webhooks.
        """
        if json is None:
            json = {}

        for resp_dict in super()._get(url=f"{self.base_url}/query", json=json):
            yield WebhookItem.model_validate(resp_dict)

    def get_by_id(self, id: str) -> WebhookItem:
        """Retrieve a webhook by their ID.

        Args:
            id (str): The ID of the webhook.

        Returns:
            (WebhookItem): The webhook item with the specified ID.
        """
        resp_dict = super()._get_by_id(url=f"{self.base_url}/{id}")
        return WebhookItem.model_validate(resp_dict)

    def update(self, item: WebhookItem) -> WebhookItem:
        """Update an existing webhook on the server.

        Args:
            item (WebhookItem): The webhook to update.

        Raises:
            ItemNotFoundError: If the webhook does not have an ID.

        Returns:
            (WebhookItem): The updated webhook.
        """
        item = WebhookItem.model_validate(item)

        if not item.id:
            raise ItemNotFoundError

        resp_dict = super()._update(
            url=f"{self.base_url}/{item.id}", json=item.update_json
        )
        return WebhookItem.model_validate(resp_dict)
