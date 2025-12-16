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
from mindbridgeapi.analysis_type_configuration_item import AnalysisTypeConfigurationItem
from mindbridgeapi.base_set import BaseSet
from mindbridgeapi.exceptions import ItemNotFoundError

if TYPE_CHECKING:
    from collections.abc import Generator


@dataclass
class AnalysisTypeConfigurations(BaseSet):
    @cached_property
    def base_url(self) -> str:
        return f"{self.server.base_url}/analysis-type-configuration"

    def get(
        self, json: dict[str, Any] | None = None
    ) -> "Generator[AnalysisTypeConfigurationItem, None, None]":
        if json is None:
            json = {}

        for resp_dict in super()._get(url=f"{self.base_url}/query", json=json):
            yield AnalysisTypeConfigurationItem.model_validate(resp_dict)

    def get_by_id(self, id: str) -> AnalysisTypeConfigurationItem:
        resp_dict = super()._get_by_id(url=f"{self.base_url}/{id}")
        return AnalysisTypeConfigurationItem.model_validate(resp_dict)

    def update(
        self, analysis_type_configuration_item: AnalysisTypeConfigurationItem
    ) -> AnalysisTypeConfigurationItem:
        analysis_type_configuration_item = AnalysisTypeConfigurationItem.model_validate(
            analysis_type_configuration_item
        )

        if not analysis_type_configuration_item.id:
            raise ItemNotFoundError

        resp_dict = super()._update(
            url=f"{self.base_url}/{analysis_type_configuration_item.id}",
            json=analysis_type_configuration_item.update_json,
        )
        return AnalysisTypeConfigurationItem.model_validate(resp_dict)
