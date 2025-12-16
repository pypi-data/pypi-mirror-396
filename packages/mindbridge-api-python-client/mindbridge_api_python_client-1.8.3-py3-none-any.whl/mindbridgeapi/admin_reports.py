#
#  Copyright MindBridge Analytics Inc. all rights reserved.
#
#  This material is confidential and may not be copied, distributed,
#  reversed engineered, decompiled or otherwise disseminated without
#  the prior written consent of MindBridge Analytics Inc.
#

from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING
from mindbridgeapi.activity_report_parameters import ActivityReportParameters
from mindbridgeapi.async_result_item import AsyncResultItem, AsyncResultType
from mindbridgeapi.base_set import BaseSet
from mindbridgeapi.exceptions import ItemError, ItemNotFoundError
from mindbridgeapi.row_usage_report_parameters import RowUsageReportParameters

if TYPE_CHECKING:
    from pathlib import Path


@dataclass
class AdminReports(BaseSet):
    """Use to interact with Admin reports.

    Typical usage of these functions would be accessed from the server, for example:
    ```py
    from datetime import datetime, timezone
    from pathlib import Path
    import mindbridgeapi as mbapi

    server = mbapi.Server(url="subdomain.mindbridge.ai", token="my_secret_token")
    row_usage_report_parameters = mbapi.RowUsageReportParameters(
        start=datetime.now(tz=timezone.utc),
        end=datetime.max.replace(tzinfo=timezone.utc),
    )
    async_result = server.admin_reports.run_row_usage_report(
        row_usage_report_parameters=row_usage_report_parameters
    )
    server.admin_reports.wait_for_export(async_result=async_result)
    output_file_path = server.admin_reports.download(
        async_result=async_result,
        output_file_path=(Path.home() / "Downloads" / "row_usage_report.csv"),
    )
    print(f"Saved to {output_file_path}")
    ```
    """

    @cached_property
    def base_url(self) -> str:
        return f"{self.server.base_url}/admin-reports"

    def run_activity_report(
        self, activity_report_parameters: ActivityReportParameters
    ) -> AsyncResultItem:
        """Run Activity Report.

        Uses the Run Activity Report MindBridge API endpoint.

        Args:
            activity_report_parameters (ActivityReportParameters): Report Parameters

        Returns:
            (AsyncResultItem): Asynchronous background job for the report
        """
        activity_report_parameters = ActivityReportParameters.model_validate(
            activity_report_parameters
        )
        resp_dict = super()._create(
            url=f"{self.base_url}/activity-report/run",
            json=activity_report_parameters.create_json,
        )
        return AsyncResultItem.model_validate(resp_dict)

    def run_row_usage_report(
        self, row_usage_report_parameters: RowUsageReportParameters
    ) -> AsyncResultItem:
        """Run Row Usage Report.

        Uses the Run Row Usage Report MindBridge API endpoint.

        Args:
            row_usage_report_parameters (RowUsageReportParameters): Report Parameters

        Returns:
            (AsyncResultItem): Asynchronous background job for the report
        """
        row_usage_report_parameters = RowUsageReportParameters.model_validate(
            row_usage_report_parameters
        )
        resp_dict = super()._create(
            url=f"{self.base_url}/row-usage-report/run",
            json=row_usage_report_parameters.create_json,
        )
        return AsyncResultItem.model_validate(resp_dict)

    def wait_for_export(
        self, async_result: AsyncResultItem, max_wait_minutes: int = 5
    ) -> None:
        """Waits for the AsyncResultItem to complete.

        Args:
            async_result (AsyncResultItem): Asynchronous background job to wait for
            max_wait_minutes (int): Maximum minutes to wait for the job to complete
        """
        async_result = AsyncResultItem.model_validate(async_result)
        if not async_result.id:
            raise ItemNotFoundError

        if async_result.type != AsyncResultType.ADMIN_REPORT:
            msg = f"{async_result.type=}."
            raise ItemError(msg)

        self.server.async_results._wait_for_async_result(
            async_result=async_result,
            max_wait_minutes=max_wait_minutes,
            init_interval_sec=5,
        )

    def download(
        self, async_result: AsyncResultItem, output_file_path: "Path"
    ) -> "Path":
        """Downloads the report file.

        Args:
            async_result (AsyncResultItem): Asynchronous background job to download
            output_file_path (Path): File to create

        Returns:
            (Path): File path of downloaded file.
        """
        async_result = AsyncResultItem.model_validate(async_result)
        if not async_result.id:
            raise ItemNotFoundError

        async_result = self.server.async_results.get_by_id(async_result.id)

        file_result_id = async_result._get_file_result_id(
            expected_type=AsyncResultType.ADMIN_REPORT
        )

        file_result = self.server.file_results.get_by_id(file_result_id)

        return self.server.file_results.export(
            file_result=file_result, output_file_path=output_file_path
        )
