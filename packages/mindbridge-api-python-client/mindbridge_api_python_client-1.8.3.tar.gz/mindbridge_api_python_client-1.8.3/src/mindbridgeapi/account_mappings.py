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
from mindbridgeapi.account_mapping_item import AccountMappingItem
from mindbridgeapi.base_set import BaseSet
from mindbridgeapi.common_validators import _convert_json_query
from mindbridgeapi.exceptions import ItemNotFoundError

if TYPE_CHECKING:
    from collections.abc import Generator


@dataclass
class AccountMappings(BaseSet):
    @cached_property
    def base_url(self) -> str:
        return f"{self.server.base_url}/account-mappings"

    def get_by_id(self, id: str) -> AccountMappingItem:
        url = f"{self.base_url}/{id}"
        resp_dict = super()._get_by_id(url=url)
        return AccountMappingItem.model_validate(resp_dict)

    def get(
        self, json: dict[str, Any] | None = None
    ) -> "Generator[AccountMappingItem, None, None]":
        mb_query_dict = _convert_json_query(json, required_key="engagementId")

        url = f"{self.base_url}/query"
        for resp_dict in super()._get(url=url, json=mb_query_dict):
            yield AccountMappingItem.model_validate(resp_dict)

    def update(self, item: AccountMappingItem) -> AccountMappingItem:
        if getattr(item, "id", None) is None:
            raise ItemNotFoundError

        url = f"{self.base_url}/{item.id}"
        resp_dict = super()._update(url=url, json=item.update_json)

        return AccountMappingItem.model_validate(resp_dict)
