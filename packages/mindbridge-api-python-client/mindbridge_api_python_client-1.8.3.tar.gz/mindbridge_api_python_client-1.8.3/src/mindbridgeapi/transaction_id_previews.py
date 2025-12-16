#
#  Copyright MindBridge Analytics Inc. all rights reserved.
#
#  This material is confidential and may not be copied, distributed,
#  reversed engineered, decompiled or otherwise disseminated without
#  the prior written consent of MindBridge Analytics Inc.
#

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any
from mindbridgeapi.base_set import BaseSet
from mindbridgeapi.transaction_id_preview_item import TransactionIdPreviewItem

if TYPE_CHECKING:
    from collections.abc import Generator


@dataclass
class TransactionIdPreviews(BaseSet):
    base_url: str = field(init=False)

    def __post_init__(self) -> None:
        self.base_url = f"{self.server.base_url}/transaction-id-previews"

    def get_by_id(self, id: str) -> TransactionIdPreviewItem:
        url = f"{self.base_url}/{id}"
        resp_dict = super()._get_by_id(url=url)

        return TransactionIdPreviewItem.model_validate(resp_dict)

    def get(
        self, json: dict[str, Any] | None = None
    ) -> "Generator[TransactionIdPreviewItem, None, None]":
        if json is None:
            json = {}

        url = f"{self.base_url}/query"
        for resp_dict in super()._get(url=url, json=json):
            yield TransactionIdPreviewItem.model_validate(resp_dict)
