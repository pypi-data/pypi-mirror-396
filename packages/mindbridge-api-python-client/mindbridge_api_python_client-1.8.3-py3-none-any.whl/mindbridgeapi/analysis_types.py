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
from mindbridgeapi.analysis_source_types import AnalysisSourceTypes
from mindbridgeapi.analysis_type_item import AnalysisTypeItem
from mindbridgeapi.base_set import BaseSet
from mindbridgeapi.exceptions import ItemNotFoundError

if TYPE_CHECKING:
    from collections.abc import Generator


@dataclass
class AnalysisTypes(BaseSet):
    @cached_property
    def base_url(self) -> str:
        return f"{self.server.base_url}/analysis-types"

    def get_by_id(self, id: str) -> AnalysisTypeItem:
        url = f"{self.base_url}/{id}"
        resp_dict = super()._get_by_id(url=url)

        analysis_type = AnalysisTypeItem.model_validate(resp_dict)
        self.restart_analysis_source_types(analysis_type)
        return analysis_type

    def get(
        self, json: dict[str, Any] | None = None
    ) -> "Generator[AnalysisTypeItem, None, None]":
        if json is None:
            json = {}

        url = f"{self.base_url}/query"
        for resp_dict in super()._get(url=url, json=json):
            analysis_type = AnalysisTypeItem.model_validate(resp_dict)
            self.restart_analysis_source_types(analysis_type)
            yield analysis_type

    def restart_analysis_source_types(
        self, analysis_type_item: AnalysisTypeItem
    ) -> None:
        if getattr(analysis_type_item, "id", None) is None:
            raise ItemNotFoundError

        if analysis_type_item.source_configurations is None:
            return

        analysis_source_type_ids = [
            x.source_type_id
            for x in analysis_type_item.source_configurations
            if x.source_type_id is not None
        ]

        if len(analysis_source_type_ids) != 0:
            analysis_type_item.analysis_source_types = AnalysisSourceTypes(
                server=self.server
            ).get(json={"id": {"$in": analysis_source_type_ids}})
