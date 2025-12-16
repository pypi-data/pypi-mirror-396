#
#  Copyright MindBridge Analytics Inc. all rights reserved.
#
#  This material is confidential and may not be copied, distributed,
#  reversed engineered, decompiled or otherwise disseminated without
#  the prior written consent of MindBridge Analytics Inc.
#

from dataclasses import dataclass
from functools import cached_property
import logging
from typing import TYPE_CHECKING, Any
from mindbridgeapi.analysis_source_item import AnalysisSourceItem
from mindbridgeapi.async_result_item import AsyncResultItem, AsyncResultType
from mindbridgeapi.base_set import BaseSet
from mindbridgeapi.exceptions import (
    ItemAlreadyExistsError,
    ItemNotFoundError,
    ParameterError,
    UnexpectedServerError,
)
from mindbridgeapi.generated_pydantic_model.model import (
    ApiEffectiveDateMetricsRead as AnalysisEffectiveDateMetrics,
    PeriodType as AnalysisEffectiveDateMetricsPeriod,
)

if TYPE_CHECKING:
    from collections.abc import Generator

logger = logging.getLogger(__name__)


@dataclass
class AnalysisSources(BaseSet):
    @cached_property
    def base_url(self) -> str:
        return f"{self.server.base_url}/analysis-sources"

    def create(self, item: AnalysisSourceItem) -> AnalysisSourceItem:
        if getattr(item, "id", None) is not None and item.id is not None:
            raise ItemAlreadyExistsError(item.id)

        url = self.base_url
        resp_dict = super()._create(url=url, json=item.create_json)
        async_result = AsyncResultItem.model_validate(resp_dict)

        if async_result.type != AsyncResultType.ANALYSIS_SOURCE_INGESTION:
            msg = f"Async Result Type: {async_result.type}."
            raise UnexpectedServerError(msg)

        if async_result.entity_id is None:
            msg = "Async Result Entity ID not returned."
            raise UnexpectedServerError(msg)

        logger.info(
            "Converting AnalysisSourceItem create response from a ApiAsyncResult to"
            " AnalysisSourceItem"
        )
        return self.get_by_id(async_result.entity_id)

    def get(
        self, json: dict[str, Any] | None = None
    ) -> "Generator[AnalysisSourceItem, None, None]":
        logger.info("get (generator has been started)")

        if json is None:
            json = {}

        url = f"{self.base_url}/query"
        for resp_dict in super()._get(url=url, json=json):
            yield AnalysisSourceItem.model_validate(resp_dict)

    def delete(self, item: AnalysisSourceItem) -> None:
        if getattr(item, "id", None) is None:
            raise ItemNotFoundError

        url = f"{self.base_url}/{item.id}"
        super()._delete(url=url)

    def effective_date_metrics(
        self,
        item: AnalysisSourceItem,
        period_type: AnalysisEffectiveDateMetricsPeriod = (
            AnalysisEffectiveDateMetricsPeriod.MONTH
        ),
    ) -> AnalysisEffectiveDateMetrics:
        if getattr(item, "id", None) is None:
            raise ItemNotFoundError

        if isinstance(period_type, str):
            period_type = period_type.strip().upper()  # type: ignore[assignment]

        try:
            period_type = AnalysisEffectiveDateMetricsPeriod(period_type)
        except ValueError as err:
            raise ParameterError(
                parameter_name="period_type",
                details="Not a valid AnalysisEffectiveDateMetricsPeriod.",
            ) from err

        url = f"{self.base_url}/{item.id}/effective-date-metrics"
        resp_dict = super()._get_by_id(
            url=url, query_parameters={"period": period_type.value}
        )
        return AnalysisEffectiveDateMetrics.model_validate(resp_dict)

    def update(self, item: AnalysisSourceItem) -> AnalysisSourceItem:
        if getattr(item, "id", None) is None:
            raise ItemNotFoundError

        url = f"{self.base_url}/{item.id}"
        resp_dict = super()._update(url=url, json=item.update_json)

        async_result = AsyncResultItem.model_validate(resp_dict)

        if async_result.type != AsyncResultType.ANALYSIS_SOURCE_INGESTION:
            msg = f"Async Result Type: {async_result.type}."
            raise UnexpectedServerError(msg)

        if async_result.entity_id is None:
            msg = "Async Result Entity ID not returned."
            raise UnexpectedServerError(msg)

        logger.info(
            "Converting AnalysisSourceItem update response from a ApiAsyncResult to"
            " AnalysisSourceItem"
        )
        return self.get_by_id(async_result.entity_id)

    def get_by_id(self, id: str) -> AnalysisSourceItem:
        url = f"{self.base_url}/{id}"
        resp_dict = super()._get_by_id(url=url)

        return AnalysisSourceItem.model_validate(resp_dict)
