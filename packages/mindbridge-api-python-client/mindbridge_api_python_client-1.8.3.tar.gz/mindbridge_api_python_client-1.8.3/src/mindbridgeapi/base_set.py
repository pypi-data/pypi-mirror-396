#
#  Copyright MindBridge Analytics Inc. all rights reserved.
#
#  This material is confidential and may not be copied, distributed,
#  reversed engineered, decompiled or otherwise disseminated without
#  the prior written consent of MindBridge Analytics Inc.
#

import contextlib
from dataclasses import dataclass
from enum import Enum, auto
from http import HTTPStatus
from itertools import count
import json
import logging
import shutil
import time
from typing import TYPE_CHECKING, Any, Optional
from urllib.parse import urlencode
from urllib3.util import Retry
from mindbridgeapi.exceptions import UnexpectedServerError, ValidationError

if TYPE_CHECKING:
    from collections.abc import Generator, Iterable
    from pathlib import Path
    from urllib3.response import BaseHTTPResponse
    from mindbridgeapi.server import Server

logger = logging.getLogger(__name__)


class PageLocation(Enum):
    """Defines where to put page in the request."""

    REQUEST_BODY = auto()
    QUERY_STRING_PARAMETER = auto()


@dataclass
class BaseSet:
    server: "Server"

    def _get_by_id(
        self, url: str, query_parameters: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        resp = self.server.http.request("GET", url, fields=query_parameters)
        self._check_response(resp=resp, url=url)
        return self._response_as_dict(resp)

    def _get(
        self,
        url: str,
        json: dict[str, Any],
        page_location: PageLocation = PageLocation.QUERY_STRING_PARAMETER,
        *,
        try_again_if_locked: bool = False,
    ) -> "Generator[dict[str, Any], None, None]":
        item_holder: list[dict[str, Any]] = []
        page_number = 0
        more_pages_to_check = True

        while item_holder or more_pages_to_check:
            if not item_holder:
                content = self._get_page(
                    url=url,
                    json=json,
                    page_number=page_number,
                    page_location=page_location,
                    try_again_if_locked=try_again_if_locked,
                )

                if not content:
                    more_pages_to_check = False
                else:
                    item_holder.extend(content)
                    page_number += 1

            if item_holder:
                yield item_holder.pop(0)

    def _get_page(
        self,
        url: str,
        json: dict[str, Any],
        page_number: int,
        page_location: PageLocation = PageLocation.QUERY_STRING_PARAMETER,
        *,
        try_again_if_locked: bool = False,
    ) -> list[dict[str, Any]]:
        if page_location == PageLocation.QUERY_STRING_PARAMETER:
            params = {"page": page_number}
            request_url = f"{url}?{urlencode(params)}"
        else:
            request_url = url
            json["page"] = page_number

        # Same as set for the PoolManager (http) in Server, but getting a page will
        # always be considered to be idempotent so we can allow repeat post requests
        retries = Retry(
            connect=3, read=3, redirect=0, other=0, allowed_methods={"POST"}
        )
        resp_dict = self._post_with_try_again_if_locked(
            url=request_url,
            json=json,
            retries=retries,
            try_again_if_locked=try_again_if_locked,
        )

        if "content" not in resp_dict or not isinstance(resp_dict["content"], list):
            msg = f"{resp_dict}."
            raise UnexpectedServerError(msg)

        return resp_dict["content"]

    @staticmethod
    def _time_sleep(sleep_seconds: float) -> None:
        """Calls time.sleep().

        This is to support monkeypatching the sleep call so no sleep is done for static
        testing.

        Args:
            sleep_seconds (float): See time.sleep
        """
        time.sleep(sleep_seconds)

    def _post_with_try_again_if_locked(
        self,
        url: str,
        json: dict[str, Any] | list[str],
        retries: Retry | None = None,
        *,
        try_again_if_locked: bool = False,
    ) -> dict[str, Any]:
        extra_ok_statuses = []
        if try_again_if_locked:
            extra_ok_statuses = [HTTPStatus.LOCKED]

        init_interval_sec = 7
        max_interval_sec = 60 * 5
        max_wait_seconds = 30 * 60
        start_time = time.monotonic()
        interval_sec = init_interval_sec

        for i in count():
            iteration_start_time = time.monotonic()
            wait_seconds = iteration_start_time - start_time
            if wait_seconds > max_wait_seconds:
                msg = (
                    f"Waited too long: {wait_seconds} seconds (over {max_wait_seconds})"
                )
                raise TimeoutError(msg)

            if retries:
                resp = self.server.http.request("POST", url, retries=retries, json=json)
            else:
                resp = self.server.http.request("POST", url, json=json)

            self._check_response(
                resp=resp, url=url, extra_ok_statuses=extra_ok_statuses
            )

            if not (try_again_if_locked and resp.status == HTTPStatus.LOCKED):
                resp_dict = self._response_as_dict(resp)
                break

            sleep_seconds = max(
                interval_sec - (time.monotonic() - iteration_start_time), 1
            )
            logger.info(
                "Waiting for about %.1f seconds as: If you receive an HTTP 423 "
                "response code while querying a table, it means MindBridge is "
                "retrieving your data. Wait a few seconds before trying again.",
                sleep_seconds,
            )
            self._time_sleep(sleep_seconds)

            if interval_sec < max_interval_sec:
                interval_sec = min(init_interval_sec * 2**i, max_interval_sec)

        return resp_dict

    def _create(
        self,
        url: str,
        json: dict[str, Any] | list[str] | None = None,
        *,
        try_again_if_locked: bool = False,
    ) -> dict[str, Any]:
        if json is None:
            json = {}

        return self._post_with_try_again_if_locked(
            url=url, json=json, try_again_if_locked=try_again_if_locked
        )

    def _delete(self, url: str, json: list[str] | None = None) -> dict[str, Any] | None:
        if not json:
            resp = self.server.http.request("DELETE", url)
            self._check_response(resp=resp, url=url)
            return None

        resp = self.server.http.request("DELETE", url, json=json)
        self._check_response(resp=resp, url=url)
        return self._response_as_dict(resp)

    def _update(self, url: str, json: dict[str, Any]) -> dict[str, Any]:
        resp = self.server.http.request("PUT", url, json=json)
        self._check_response(resp=resp, url=url)
        return self._response_as_dict(resp)

    def _upload(self, url: str, files: dict[str, Any]) -> dict[str, Any]:
        resp = self.server.http.request("POST", url, fields=files)

        self._check_response(resp=resp, url=url)
        return self._response_as_dict(resp)

    @staticmethod
    def _response_decoded(resp: "BaseHTTPResponse") -> Any:
        """JSON as decoded to Python.

        Plan to refactor this as part of AIA-32145

        Args:
            resp (urllib3.response.BaseHTTPResponse): The HTTP response from the server

        Returns:
            (Any): The representation of the JSON response from the server

        Raises:
            UnexpectedServerError: When the response is not JSON
        """
        if resp.status == HTTPStatus.NO_CONTENT:
            # No body expected, so the return value won't be used
            return {}

        try:
            resp_obj = json.loads(resp.data)
        except UnicodeDecodeError as err:
            msg = "body does not contain UTF-8, UTF-16 or UTF-32 encoded data."
            raise UnexpectedServerError(msg) from err
        except json.JSONDecodeError as err:
            msg = "body is not a valid JSON document."
            raise UnexpectedServerError(msg) from err

        return resp_obj

    @staticmethod
    def _response_as_dict(resp: "BaseHTTPResponse") -> dict[str, Any]:
        """Converts the HTTP response body as a dict.

        Plan to refactor this as part of AIA-32145

        Args:
            resp (urllib3.response.BaseHTTPResponse): The HTTP response from the server

        Returns:
            (Dict[str, Any]): The dict representation of the JSON response from the
                server

        Raises:
            UnexpectedServerError: When the response is JSON but Python didn't parase
                the data to a dict
        """
        resp_obj = BaseSet._response_decoded(resp)

        if not isinstance(resp_obj, dict):
            msg = "JSON was not an object."
            raise UnexpectedServerError(msg)

        return resp_obj

    def _download(self, url: str, output_path: "Path") -> "Path":
        with (
            self.server.http.request("GET", url, preload_content=False) as resp,
            output_path.open("wb") as write_file,
        ):
            shutil.copyfileobj(resp, write_file)
            self._check_response(resp=resp, url=url)
            resp.release_conn()

        return output_path

    @staticmethod
    def _check_response(
        resp: "BaseHTTPResponse",
        url: str,
        extra_ok_statuses: Optional["Iterable[int]"] = None,
    ) -> None:
        """Raises error if response status is not ok, also logs.

        Raises:
            ValidationError: If 400 response
            UnexpectedServerError: If 500 response
        """
        if extra_ok_statuses is None:
            extra_ok_statuses = iter(())

        http_code_phrase = f"{resp.status} {HTTPStatus(resp.status).phrase}"

        log_str = "HTTP response (approximately):"
        log_str += f"\n{http_code_phrase}"
        for k, v in resp.headers.items():
            log_str += f"\n{k}: {v}"

        log_str += "\n"
        try:
            log_str += (
                f"\n{json.dumps(json.loads(resp.data), indent=4, sort_keys=True)}"
            )
        except (UnicodeDecodeError, json.JSONDecodeError):
            if len(resp.data) > 0:
                log_str += "\n[Body that is apparently not JSON data]"

        logger.debug(log_str)

        # Raise error if not ok
        if (
            resp.status >= HTTPStatus.BAD_REQUEST
            and resp.status not in extra_ok_statuses
        ):
            http_error_msg = f"{http_code_phrase} for url: {url}"
            with contextlib.suppress(UnicodeDecodeError, json.JSONDecodeError):
                http_error_msg += (
                    f"\n{json.dumps(json.loads(resp.data), indent=4, sort_keys=True)}."
                )

            if resp.status < HTTPStatus.INTERNAL_SERVER_ERROR:
                raise ValidationError(http_error_msg)

            raise UnexpectedServerError(http_error_msg)

    def _post_expect_list(self, url: str, json: dict[str, Any]) -> list[dict[str, Any]]:
        resp = self.server.http.request("POST", url, json=json)
        return self._response_as_list(url=url, resp=resp)

    def _get_by_id_expect_list(
        self, url: str, query_parameters: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        resp = self.server.http.request("GET", url, fields=query_parameters)
        return self._response_as_list(url=url, resp=resp)

    def _response_as_list(
        self, url: str, resp: "BaseHTTPResponse"
    ) -> list[dict[str, Any]]:
        self._check_response(resp=resp, url=url)
        resp_obj = self._response_decoded(resp=resp)

        if not isinstance(resp_obj, list):
            msg = "JSON was not an array."
            raise UnexpectedServerError(msg)

        return resp_obj
