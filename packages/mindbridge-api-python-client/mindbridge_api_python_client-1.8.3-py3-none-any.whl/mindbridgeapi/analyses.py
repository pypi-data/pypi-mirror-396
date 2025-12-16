#
#  Copyright MindBridge Analytics Inc. all rights reserved.
#
#  This material is confidential and may not be copied, distributed,
#  reversed engineered, decompiled or otherwise disseminated without
#  the prior written consent of MindBridge Analytics Inc.
#

from dataclasses import dataclass
from datetime import date
from functools import cached_property
import logging
from typing import TYPE_CHECKING, Any
from mindbridgeapi.analysis_item import AnalysisItem
from mindbridgeapi.analysis_results import AnalysisResults
from mindbridgeapi.analysis_sources import AnalysisSources
from mindbridgeapi.async_result_item import AsyncResultItem, AsyncResultType
from mindbridgeapi.base_set import BaseSet
from mindbridgeapi.data_tables import DataTables
from mindbridgeapi.exceptions import (
    ItemAlreadyExistsError,
    ItemError,
    ItemNotFoundError,
    ParameterError,
    UnexpectedServerError,
    ValidationError,
)
from mindbridgeapi.generated_pydantic_model.model import (
    ApiAnalysisStatusRead,
    ApiEngagementRollForwardRequest,
    EntityType,
)
from mindbridgeapi.tasks import Tasks

if TYPE_CHECKING:
    from collections.abc import Generator
    from mindbridgeapi.engagement_item import EngagementItem

logger = logging.getLogger(__name__)


@dataclass
class Analyses(BaseSet):
    @cached_property
    def base_url(self) -> str:
        return f"{self.server.base_url}/analyses"

    def create(self, item: AnalysisItem) -> AnalysisItem:
        if getattr(item, "id", None) is not None and item.id is not None:
            raise ItemAlreadyExistsError(item.id)

        url = self.base_url
        resp_dict = super()._create(url=url, json=item.create_json)
        analysis = AnalysisItem.model_validate(resp_dict)
        return self._restart_all_children(analysis)

    def update(self, item: AnalysisItem) -> AnalysisItem:
        if getattr(item, "id", None) is None:
            raise ItemNotFoundError

        url = f"{self.base_url}/{item.id}"
        resp_dict = super()._update(url=url, json=item.update_json)

        analysis = AnalysisItem.model_validate(resp_dict)
        return self._restart_all_children(analysis)

    def get(
        self, json: dict[str, Any] | None = None
    ) -> "Generator[AnalysisItem, None, None]":
        if json is None:
            json = {}

        url = f"{self.base_url}/query"
        for resp_dict in super()._get(url=url, json=json):
            analysis = AnalysisItem.model_validate(resp_dict)
            yield self._restart_all_children(analysis)

    def delete(self, item: AnalysisItem) -> None:
        if getattr(item, "id", None) is None:
            raise ItemNotFoundError

        url = f"{self.base_url}/{item.id}"
        super()._delete(url=url)

    def run(self, item: AnalysisItem) -> AnalysisItem:
        analysis_id = getattr(item, "id", None)
        if analysis_id is None:
            raise ItemNotFoundError

        url = f"{self.base_url}/{analysis_id}/run"
        _ = super()._create(url=url)

        return self.get_by_id(analysis_id)

    def wait_for_analysis_sources(
        self, analysis: AnalysisItem, max_wait_minutes: int = 24 * 60
    ) -> AnalysisItem:
        analysis_id = getattr(analysis, "id", None)
        if analysis_id is None:
            raise ItemNotFoundError

        analysis = self.get_by_id(analysis_id)

        if getattr(analysis, "id", None) != analysis_id:
            msg = "analysis id was not the same as requested."
            raise UnexpectedServerError(msg)

        analysis_sources = list(analysis.analysis_sources)
        if not analysis_sources:
            msg = "Analysis has no analysis sources to wait for."
            raise ItemError(msg)

        # Get the list of async_result ids
        async_results_to_check = []
        for analysis_source in analysis_sources:
            async_results = self.server.async_results.get(
                json={
                    "$and": [
                        {"entityId": {"$eq": analysis_source.id}},
                        {"type": {"$eq": AsyncResultType.ANALYSIS_SOURCE_INGESTION}},
                        {"entityType": {"$eq": EntityType.ANALYSIS_SOURCE}},
                    ]
                }
            )
            async_results_list = list(async_results)
            if len(async_results_list) == 0:
                """
                This shouldn't occur as analysis sources are started as soon as they are
                added to the analysis
                """
                msg = (
                    f"Unable to find {EntityType.ANALYSIS_SOURCE} status for: "
                    f"{analysis_source.id}."
                )
                raise UnexpectedServerError(msg)

            async_result = max(
                async_results_list,
                key=lambda x: getattr(x, "last_modified_date", date.min),
            )
            async_results_to_check.append(async_result)

        self.server.async_results._wait_for_async_results(
            async_results=async_results_to_check,
            max_wait_minutes=max_wait_minutes,
            init_interval_sec=11,
        )

        analysis_status = self.status(analysis)
        analysis_status_ready = getattr(analysis_status, "ready", False)
        analysis_status_preflight_errors = getattr(
            analysis_status, "preflight_errors", []
        )
        if analysis_status_ready:
            logger.info("Analysis (%s) is ready to run", analysis_id)
        else:
            err_msg = f"Analysis ({analysis_id}) is not ready to run"
            if len(analysis_status_preflight_errors) == 0:
                err_msg = f"{err_msg} (no preflight_errors)"
            else:
                preflight_errors_str = ", ".join(
                    [str(i.name) for i in analysis_status_preflight_errors]
                )
                err_msg = f"{err_msg}. Preflight Errors: {preflight_errors_str}."

            raise ValidationError(err_msg)

        return self.get_by_id(analysis_id)

    def status(self, item: AnalysisItem) -> ApiAnalysisStatusRead:
        if getattr(item, "id", None) is None:
            raise ItemNotFoundError

        url = f"{self.base_url}/{item.id}/status"
        resp_dict = super()._get_by_id(url=url)
        analysis_status = ApiAnalysisStatusRead.model_validate(resp_dict)

        self._status_log_message(item, analysis_status)

        return analysis_status

    @staticmethod
    def _status_log_message(
        analysis: AnalysisItem, analysis_status_item: ApiAnalysisStatusRead
    ) -> None:
        log_message = f"Analysis Status for {analysis.name} ({analysis.id}):"
        log_message += f"\n    ready: {analysis_status_item.ready}"
        log_message += f"\n    status: {analysis_status_item.status}"
        log_message += (
            "\n    unmapped_account_mapping_count:"
            f" {analysis_status_item.unmapped_account_mapping_count}"
        )
        log_message += (
            "\n    mapped_account_mapping_count:"
            f" {analysis_status_item.mapped_account_mapping_count}"
        )
        log_message += (
            "\n    inferred_account_mapping_count:"
            f" {analysis_status_item.inferred_account_mapping_count}"
        )
        log_message += "\n    preflight_errors:"
        for pfe in getattr(analysis_status_item, "preflight_errors", []):
            log_message += f"\n    - {pfe}"

        log_message += "\n    source_statuses:"
        for source_status in getattr(analysis_status_item, "source_statuses", []):
            log_message += f"\n    - source_id: {source_status.source_id}"
            log_message += f"\n    - status: {source_status.status}"
            log_message += (
                "\n    - analysis_source_type_id:"
                f" {source_status.analysis_source_type_id}"
            )
            log_message += f"\n    - period_id: {source_status.period_id}"
            log_message += "\n"

        logger.info(log_message)

    def wait_for_analysis(
        self, analysis: AnalysisItem, max_wait_minutes: int = 24 * 60
    ) -> AnalysisItem:
        if analysis.id is None:
            raise ItemNotFoundError

        self.restart_analysis_results(analysis)
        analysis_results_list = list(analysis.analysis_results)
        if not analysis_results_list:
            msg = (
                f"Unable to find any analysis_results for: {analysis.id}. Possibly the "
                "analysis has not been started yet?"
            )
            raise ValidationError(msg)

        analysis_result = max(
            analysis_results_list, key=lambda x: getattr(x, "creation_date", date.min)
        )

        async_results = self.server.async_results.get(
            json={
                "$and": [
                    {"entityId": {"$eq": analysis_result.id}},
                    {"type": {"$eq": AsyncResultType.ANALYSIS_RUN}},
                    {"entityType": {"$eq": EntityType.ANALYSIS_RESULT}},
                ]
            }
        )
        async_results_list = list(async_results)
        if not async_results_list:
            msg = (
                f"Unable to find {AsyncResultType.ANALYSIS_RUN} for: {analysis.id}."
                " Possibly the analysis has not been started yet?"
            )
            raise ValidationError(msg)

        async_result = max(
            async_results_list, key=lambda x: getattr(x, "last_modified_date", date.min)
        )

        self.server.async_results._wait_for_async_result(
            async_result=async_result,
            max_wait_minutes=max_wait_minutes,
            init_interval_sec=76,
        )

        return self.get_by_id(analysis.id)

    def roll_forward_analysis_to_engagement(
        self,
        analysis_item: AnalysisItem,
        engagement_item: "EngagementItem",
        *,
        interim: bool = False,
    ) -> AnalysisItem:
        url = f"{self.base_url}/engagement-roll-forward"

        if analysis_item.id is None or analysis_item.engagement_id is None:
            raise ItemNotFoundError

        if engagement_item.id is None:
            raise ItemNotFoundError

        if analysis_item.engagement_id == engagement_item.id:
            raise ParameterError(
                parameter_name="engagement_id",
                details=(
                    "The target engagement cannot be the same engagement in which the "
                    "analysis exists."
                ),
            )

        roll_forward_request = ApiEngagementRollForwardRequest(
            analysis_id=analysis_item.id,
            interim=interim,
            target_engagement_id=engagement_item.id,
        )
        roll_forward_request_json = roll_forward_request.model_dump(
            mode="json", by_alias=True, exclude_none=True
        )
        resp_dict = super()._create(url=url, json=roll_forward_request_json)
        async_result = AsyncResultItem.model_validate(resp_dict)
        if async_result.entity_id is None:
            raise UnexpectedServerError(details="async_result.entity_id was None.")

        return self.get_by_id(async_result.entity_id)

    def get_by_id(self, id: str) -> AnalysisItem:
        url = f"{self.base_url}/{id}"
        resp_dict = super()._get_by_id(url=url)
        analysis = AnalysisItem.model_validate(resp_dict)
        return self._restart_all_children(analysis)

    def _restart_all_children(self, analysis: AnalysisItem) -> AnalysisItem:
        self.restart_analysis_results(analysis)
        self.restart_analysis_sources(analysis)
        self.restart_data_tables(analysis)
        self.restart_tasks(analysis)

        return analysis

    def restart_analysis_results(self, analysis: AnalysisItem) -> None:
        if analysis.id is None:
            raise ItemNotFoundError

        analysis.analysis_results = AnalysisResults(server=self.server).get(
            json={"analysisId": {"$eq": analysis.id}}
        )

    def restart_analysis_sources(self, analysis_item: AnalysisItem) -> None:
        if getattr(analysis_item, "id", None) is None:
            raise ItemNotFoundError

        analysis_item.analysis_sources = AnalysisSources(server=self.server).get(
            json={"analysisId": {"$eq": analysis_item.id}}
        )

    def restart_data_tables(self, analysis_item: AnalysisItem) -> None:
        if getattr(analysis_item, "id", None) is None:
            raise ItemNotFoundError

        analysis_item.data_tables = DataTables(server=self.server).get(
            json={"analysisId": {"$eq": analysis_item.id}}
        )

    def restart_tasks(self, analysis_item: AnalysisItem) -> None:
        if getattr(analysis_item, "id", None) is None:
            raise ItemNotFoundError

        analysis_item.tasks = Tasks(server=self.server).get(
            json={"analysisId": {"$eq": analysis_item.id}}
        )
