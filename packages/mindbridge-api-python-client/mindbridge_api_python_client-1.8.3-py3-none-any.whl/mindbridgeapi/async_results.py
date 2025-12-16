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
import time
from typing import TYPE_CHECKING, Any
from mindbridgeapi.async_result_item import AsyncResultItem, AsyncResultStatus
from mindbridgeapi.base_set import BaseSet
from mindbridgeapi.exceptions import (
    ItemNotFoundError,
    UnexpectedServerError,
    ValidationError,
)

if TYPE_CHECKING:
    from collections.abc import Generator

logger = logging.getLogger(__name__)


@dataclass
class AsyncResults(BaseSet):
    @cached_property
    def base_url(self) -> str:
        return f"{self.server.base_url}/async-results"

    def _wait_for_async_result(
        self,
        async_result: AsyncResultItem,
        max_wait_minutes: int,
        init_interval_sec: int,
    ) -> None:
        """Wait for async result to complete.

        Waits, at most the minutes specified, for the async result to be COMPLETE and
        raises and error if any error

        Args:
            async_result (AsyncResultItem): Async result to check
            max_wait_minutes (int): Maximum minutes to wait
            init_interval_sec (int): The initial seconds to wait
        """
        self._wait_for_async_results(
            async_results=[async_result],
            max_wait_minutes=max_wait_minutes,
            init_interval_sec=init_interval_sec,
        )

    @staticmethod
    def _wait_for_async_results_refresh_sorted_ids(
        async_results: list[AsyncResultItem],
    ) -> list[str]:
        async_result_ids = []
        for async_result in async_results:
            if async_result.id is None:
                raise ItemNotFoundError

            async_result_ids.append(async_result.id)

        return sorted(async_result_ids)

    def _wait_for_async_results_refresh(
        self, async_results: list[AsyncResultItem]
    ) -> list[AsyncResultItem]:
        if not async_results:
            return []

        sorted_async_result_ids = self._wait_for_async_results_refresh_sorted_ids(
            async_results=async_results
        )

        new_async_results = list(
            self.get(json={"id": {"$in": sorted_async_result_ids}})
        )

        sorted_new_async_result_ids = self._wait_for_async_results_refresh_sorted_ids(
            async_results=new_async_results
        )

        if sorted_async_result_ids != sorted_new_async_result_ids:
            msg = (
                f"AsyncResults received didn't match: {sorted_async_result_ids=}, "
                f"{sorted_new_async_result_ids=}."
            )
            raise UnexpectedServerError(msg)

        return new_async_results

    def _wait_for_async_results(
        self,
        async_results: list[AsyncResultItem],
        max_wait_minutes: int,
        init_interval_sec: int,
    ) -> None:
        """Wait for async results to complete.

        Waits, at most the minutes specified, for all async results to be COMPLETE and
        raises and error if any error

        Args:
            async_results (List[AsyncResultItem]): Async results to check
            max_wait_minutes (int): Maximum minutes to wait
            init_interval_sec (int): The initial seconds to wait

        Raises:
            TimeoutError: If waited for more than specified
        """
        max_interval_sec = 60 * 5
        max_wait_seconds = max_wait_minutes * 60
        start_time = time.monotonic()
        elapsed_time = 0.0
        interval_sec = init_interval_sec
        i = 0

        while (time.monotonic() - start_time) < max_wait_seconds:
            loop_start_time = time.monotonic()
            elapsed_time = loop_start_time - start_time

            logger.info(
                "Starting a AsyncResult iteration. It has been: %.1f seconds. Loop %i "
                "and %i to check",
                elapsed_time,
                i,
                len(async_results),
            )

            if not async_results:
                break

            new_async_results = [
                async_result
                for async_result in self._wait_for_async_results_refresh(
                    async_results=async_results
                )
                if not async_result._check_if_completed()
            ]

            if not new_async_results:
                break

            sleep_seconds = max(interval_sec - (time.monotonic() - loop_start_time), 1)
            logger.info(
                "Waiting for about %.1f seconds as some of the async results are not "
                "complete yet.",
                sleep_seconds,
            )
            self._time_sleep(sleep_seconds)

            elapsed_time = time.monotonic() - start_time

            if interval_sec < max_interval_sec:
                interval_sec = min(init_interval_sec * 2**i, max_interval_sec)

            i += 1

            logger.info(
                "Finished a AsyncResults iteration. It has been: %.1f seconds",
                elapsed_time,
            )

        else:
            msg = f"Waited too long: {max_wait_minutes} minutes."
            raise TimeoutError(msg)

    @staticmethod
    def _check_if_async_result_is_completed(async_result: AsyncResultItem) -> bool:
        """Checks if the Async Result is completed.

        Returns True if COMPLETE, False if IN_PROGRESS and raises and error otherwise.

        Args:
            async_result (AsyncResultItem): The async result to check

        Returns:
            bool: True if COMPLETE, False if IN_PROGRESS

        Raises:
            ValidationError: If the async_result resulted in an error state
        """
        async_result_str = (
            f"Async Result {async_result.id} for"
            f" {async_result.entity_type} {async_result.entity_id} resulted in"
            f" {async_result.status}"
        )
        logger.info(async_result_str)

        if async_result.status == AsyncResultStatus.IN_PROGRESS:
            return False

        if async_result.status == AsyncResultStatus.COMPLETE:
            return True

        # Must be AsyncResultStatus.ERROR
        msg = f"{async_result_str} with message {async_result.error}."
        raise ValidationError(msg)

    def get(
        self, json: dict[str, Any] | None = None
    ) -> "Generator[AsyncResultItem, None, None]":
        if json is None:
            json = {}

        url = f"{self.base_url}/query"
        for resp_dict in super()._get(url=url, json=json):
            yield AsyncResultItem.model_validate(resp_dict)

    def get_by_id(self, id: str) -> AsyncResultItem:
        url = f"{self.base_url}/{id}"
        resp_dict = super()._get_by_id(url=url)

        return AsyncResultItem.model_validate(resp_dict)
