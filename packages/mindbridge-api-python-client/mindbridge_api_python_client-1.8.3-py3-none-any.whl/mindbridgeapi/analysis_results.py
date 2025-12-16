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
from mindbridgeapi.analysis_result_item import AnalysisResultItem
from mindbridgeapi.base_set import BaseSet

if TYPE_CHECKING:
    from collections.abc import Generator


@dataclass
class AnalysisResults(BaseSet):
    @cached_property
    def base_url(self) -> str:
        return f"{self.server.base_url}/analysis-results"

    def get_by_id(self, id: str) -> AnalysisResultItem:
        url = f"{self.base_url}/{id}"
        resp_dict = super()._get_by_id(url=url)

        return AnalysisResultItem.model_validate(resp_dict)

    def get(
        self, json: dict[str, Any] | None = None
    ) -> "Generator[AnalysisResultItem, None, None]":
        if json is None:
            json = {}

        url = f"{self.base_url}/query"
        for resp_dict in super()._get(url=url, json=json):
            yield AnalysisResultItem.model_validate(resp_dict)
