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
from mindbridgeapi.engagements import Engagements
from mindbridgeapi.exceptions import ItemAlreadyExistsError, ItemNotFoundError
from mindbridgeapi.organization_item import OrganizationItem

if TYPE_CHECKING:
    from collections.abc import Generator


@dataclass
class Organizations(BaseSet):
    """Use to interact with Organizations.

    Typical usage of these functions would be accessed from the server, for example:
    ```py
    import mindbridgeapi as mbapi

    server = mbapi.Server(url="subdomain.mindbridge.ai", token="my_secret_token")
    organization = mbapi.OrganizationItem(name="My Organization Name")
    organization = server.organizations.create(organization)
    print(f"Created {organization.name!r}")
    ```
    """

    @cached_property
    def base_url(self) -> str:
        return f"{self.server.base_url}/organizations"

    def create(self, item: OrganizationItem) -> OrganizationItem:
        """Create a new organization.

        Uses the Create Organization MindBridge API endpoint.

        Args:
            item (OrganizationItem): Organization to create

        Returns:
            (OrganizationItem): Organization as created

        Raises:
            ItemAlreadyExistsError: If the OrganizationItem provided already had and id
        """
        if getattr(item, "id", None) is not None and item.id is not None:
            raise ItemAlreadyExistsError(item.id)

        url = self.base_url
        resp_dict = super()._create(url=url, json=item.create_json)
        organization = OrganizationItem.model_validate(resp_dict)
        self.restart_engagements(organization)

        return organization

    def get_by_id(self, id: str) -> OrganizationItem:
        """Get an Organization.

        Uses the Read Organization MindBridge API endpoint.

        Args:
            id (str): id of the Organization to get

        Returns:
            (OrganizationItem): Organization requested
        """
        url = f"{self.base_url}/{id}"
        resp_dict = super()._get_by_id(url=url)

        organization = OrganizationItem.model_validate(resp_dict)
        self.restart_engagements(organization)

        return organization

    def update(self, item: OrganizationItem) -> OrganizationItem:
        if getattr(item, "id", None) is None:
            raise ItemNotFoundError

        url = f"{self.base_url}/{item.id}"
        resp_dict = super()._update(url=url, json=item.update_json)

        organization = OrganizationItem.model_validate(resp_dict)
        self.restart_engagements(organization)

        return organization

    def get(
        self, json: dict[str, Any] | None = None
    ) -> "Generator[OrganizationItem, None, None]":
        if json is None:
            json = {}

        url = f"{self.base_url}/query"
        for resp_dict in super()._get(url=url, json=json):
            organization = OrganizationItem.model_validate(resp_dict)
            self.restart_engagements(organization)

            yield organization

    def restart_engagements(self, org_item: OrganizationItem) -> None:
        if getattr(org_item, "id", None) is None:
            raise ItemNotFoundError

        org_item.engagements = Engagements(server=self.server).get(
            json={"organizationId": {"$eq": org_item.id}}
        )

    def delete(self, item: OrganizationItem) -> None:
        if getattr(item, "id", None) is None:
            raise ItemNotFoundError

        url = f"{self.base_url}/{item.id}"
        super()._delete(url=url)
