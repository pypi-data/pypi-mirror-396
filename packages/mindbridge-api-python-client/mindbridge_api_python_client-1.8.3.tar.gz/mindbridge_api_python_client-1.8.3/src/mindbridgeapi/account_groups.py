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
from mindbridgeapi.account_group_item import AccountGroupItem
from mindbridgeapi.base_set import BaseSet
from mindbridgeapi.common_validators import _convert_json_query
from mindbridgeapi.exceptions import ItemNotFoundError

if TYPE_CHECKING:
    from collections.abc import Generator


@dataclass
class AccountGroups(BaseSet):
    @cached_property
    def base_url(self) -> str:
        return f"{self.server.base_url}/account-groups"

    def get_by_id(self, id: str) -> AccountGroupItem:
        url = f"{self.base_url}/{id}"
        resp_dict = super()._get_by_id(url=url)

        return AccountGroupItem.model_validate(resp_dict)

    def get(
        self, json: dict[str, Any] | None = None
    ) -> "Generator[AccountGroupItem, None, None]":
        mb_query_dict = _convert_json_query(json, required_key="accountGroupingId")

        url = f"{self.base_url}/query"
        for resp_dict in super()._get(url=url, json=mb_query_dict):
            yield AccountGroupItem.model_validate(resp_dict)

    def update(self, account_group: AccountGroupItem) -> AccountGroupItem:
        if getattr(account_group, "id", None) is None:
            raise ItemNotFoundError

        url = f"{self.base_url}/{account_group.id}"
        resp_dict = super()._update(url=url, json=account_group.update_json)

        return AccountGroupItem.model_validate(resp_dict)
