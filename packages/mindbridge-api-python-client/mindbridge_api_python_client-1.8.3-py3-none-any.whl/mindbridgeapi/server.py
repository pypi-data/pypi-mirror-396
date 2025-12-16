#
#  Copyright MindBridge Analytics Inc. all rights reserved.
#
#  This material is confidential and may not be copied, distributed,
#  reversed engineered, decompiled or otherwise disseminated without
#  the prior written consent of MindBridge Analytics Inc.
#

from ast import literal_eval
from dataclasses import dataclass, field
from functools import cached_property
import http.client
import json
import logging
from ssl import CERT_NONE, CERT_REQUIRED
from urllib3 import PoolManager
from urllib3.util import Retry, Url, make_headers, parse_url
from mindbridgeapi.account_groupings import AccountGroupings
from mindbridgeapi.account_groups import AccountGroups
from mindbridgeapi.account_mappings import AccountMappings
from mindbridgeapi.admin_reports import AdminReports
from mindbridgeapi.analyses import Analyses
from mindbridgeapi.analysis_results import AnalysisResults
from mindbridgeapi.analysis_source_types import AnalysisSourceTypes
from mindbridgeapi.analysis_sources import AnalysisSources
from mindbridgeapi.analysis_type_configurations import AnalysisTypeConfigurations
from mindbridgeapi.analysis_types import AnalysisTypes
from mindbridgeapi.api_tokens import ApiTokens
from mindbridgeapi.async_results import AsyncResults
from mindbridgeapi.chunked_files import ChunkedFiles
from mindbridgeapi.data_tables import DataTables
from mindbridgeapi.engagement_account_groupings import EngagementAccountGroupings
from mindbridgeapi.engagement_account_groups import EngagementAccountGroups
from mindbridgeapi.engagements import Engagements
from mindbridgeapi.file_infos import FileInfos
from mindbridgeapi.file_manager import FileManager
from mindbridgeapi.file_results import FileResults
from mindbridgeapi.json_tables import JSONTables
from mindbridgeapi.libraries import Libraries
from mindbridgeapi.organizations import Organizations
from mindbridgeapi.populations import Populations
from mindbridgeapi.risk_ranges import RiskRanges
from mindbridgeapi.task_histories import TaskHistories
from mindbridgeapi.tasks import Tasks
from mindbridgeapi.transaction_id_previews import TransactionIdPreviews
from mindbridgeapi.users import Users
from mindbridgeapi.version import VERSION, get_package_name
from mindbridgeapi.webhooks import Webhooks

logger = logging.getLogger(__name__)


def _print_to_log(*args: str) -> None:
    """Overrides the `print` function in http.client to log instead.

    This function is meant to override the print function in
    [http.client](https://docs.python.org/3/library/http.client.html). In this module
    the debugging information is available by setting
    `http.client.HTTPConnection.debuglevel` to a non-zero value, which then uses the
    `print` function to display details. So, by overriding this method we can instead
    use the logging module to log this information instead. This function also only logs
    the "send:" data and logs the information in a more usable format.

    Args:
        args (Tuple[str]): args used in the print function of http.client
    """
    if not (log_str := _validate_and_get_logstr(*args)):
        return

    try:
        log_bytes = literal_eval(log_str)
    except (ValueError, TypeError, SyntaxError, MemoryError, RecursionError):
        logger.debug("Unable to evaluate the HTTP sent data: unable to evaluate repr")
        return

    if not isinstance(log_bytes, bytes):
        logger.debug("Unable to evaluate the HTTP sent data: not bytes")
        return

    if log_str.startswith("b'--"):
        _log_multipart(log_bytes)
        return

    pretty_json = _pretty_json(log_bytes)
    if pretty_json is not None:
        logger.debug("HTTP approximate sent body:\n%s", pretty_json)
        return

    headers = _headers_to_log_str(log_bytes)
    logger.debug("HTTP approximate sent headers:\n%s", headers)


def _validate_and_get_logstr(*args: str) -> str | None:
    expected_number_of_args = 2
    if not isinstance(args, tuple) or len(args) != expected_number_of_args:
        return None

    first_arg, log_str = args
    if first_arg != "send:":
        return None

    if not isinstance(log_str, str):
        logger.debug(
            "Unable to evaluate the HTTP sent data: The print parameter was not str"
        )
        return None

    return log_str


def _log_multipart(log_bytes: bytes) -> None:
    boundry_bytes = log_bytes.partition(b"\r\n")[0]
    try:
        boundry_str = boundry_bytes.decode()
    except UnicodeDecodeError:
        boundry_str = f"unable to decode bytes: {boundry_bytes!r}"

    logger.debug("Parsing multipart with boundary %s", boundry_str)
    for i, content in enumerate(log_bytes.split(boundry_bytes)):
        log_str_prefix = (
            f"HTTP approximate multipart (boundary {boundry_str} partition {i})"
        )

        if i == 0 or content == b"--\r\n":
            # first occourance, content will be empty
            # last occourance, content is almost empty like above
            continue

        paritioned_content = content.partition(b"\r\n\r\n")

        headers = _headers_to_log_str(paritioned_content[0])
        logger.debug("%s headers:\n%s", log_str_prefix, headers)

        pretty_json = _pretty_json(paritioned_content[2])
        if pretty_json is not None:
            logger.debug("%s body:\n%s", log_str_prefix, pretty_json)
        else:
            logger.debug("%s body:\n[Redacted as it was not JSON data]", log_str_prefix)


def _pretty_json(in_bytes: bytes) -> str | None:
    try:
        body_obj = json.loads(in_bytes)
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None

    return json.dumps(body_obj, indent=4, sort_keys=True)


def _headers_to_log_str(log_bytes: bytes) -> str:
    prefix = "authorization: Bearer "
    line_strs = []
    for line in log_bytes.splitlines():
        if len(line) == 0:
            continue

        try:
            line_str = line.decode()
        except UnicodeDecodeError:
            line_str = f"unable to decode bytes: {line!r}"

        if line_str.startswith(prefix):
            line_str = prefix + "[REDACTED]"

        line_strs.append(line_str)

    return "\n".join(line_strs)


@dataclass
class Server:
    url: str  # Provided URL, like mycompany.mindbridge.ai
    token: str = field(repr=False)  # API token
    verify_certificate: bool = (
        True  # If False don't verify the SSL certificate (cert_reqs=CERT_NONE)
    )
    http: PoolManager = field(init=False, repr=False)
    account_groupings: AccountGroupings = field(init=False, repr=False)
    account_groups: AccountGroups = field(init=False, repr=False)
    account_mappings: AccountMappings = field(init=False, repr=False)
    admin_reports: AdminReports = field(init=False, repr=False)
    analyses: Analyses = field(init=False, repr=False)
    analysis_results: AnalysisResults = field(init=False, repr=False)
    analysis_source_types: AnalysisSourceTypes = field(init=False, repr=False)
    analysis_sources: AnalysisSources = field(init=False, repr=False)
    analysis_type_configurations: AnalysisTypeConfigurations = field(
        init=False, repr=False
    )
    analysis_types: AnalysisTypes = field(init=False, repr=False)
    api_tokens: ApiTokens = field(init=False, repr=False)
    async_results: AsyncResults = field(init=False, repr=False)
    chunked_files: ChunkedFiles = field(init=False, repr=False)
    data_tables: DataTables = field(init=False, repr=False)
    engagement_account_groupings: EngagementAccountGroupings = field(
        init=False, repr=False
    )
    engagement_account_groups: EngagementAccountGroups = field(init=False, repr=False)
    engagements: Engagements = field(init=False, repr=False)
    file_infos: FileInfos = field(init=False, repr=False)
    file_manager: FileManager = field(init=False, repr=False)
    file_results: FileResults = field(init=False, repr=False)
    json_tables: JSONTables = field(init=False, repr=False)
    libraries: Libraries = field(init=False, repr=False)
    organizations: Organizations = field(init=False, repr=False)
    populations: Populations = field(init=False, repr=False)
    risk_ranges: RiskRanges = field(init=False, repr=False)
    task_histories: TaskHistories = field(init=False, repr=False)
    tasks: Tasks = field(init=False, repr=False)
    transaction_id_previews: TransactionIdPreviews = field(init=False, repr=False)
    users: Users = field(init=False, repr=False)
    webhooks: Webhooks = field(init=False, repr=False)

    def __post_init__(self) -> None:
        user_agent = f"{get_package_name()}/{VERSION}"

        headers = make_headers(accept_encoding=True, user_agent=user_agent)

        headers["authorization"] = "Bearer " + self.token

        # redirect=0 as the base url will always be https
        retries = Retry(connect=3, read=3, redirect=0, other=0)

        cert_reqs = CERT_REQUIRED  # default
        if not self.verify_certificate:
            cert_reqs = CERT_NONE

        self.http = PoolManager(headers=headers, retries=retries, cert_reqs=cert_reqs)

        self.account_groupings = AccountGroupings(server=self)
        self.account_groups = AccountGroups(server=self)
        self.account_mappings = AccountMappings(server=self)
        self.admin_reports = AdminReports(server=self)
        self.analyses = Analyses(server=self)
        self.analysis_results = AnalysisResults(server=self)
        self.analysis_source_types = AnalysisSourceTypes(server=self)
        self.analysis_sources = AnalysisSources(server=self)
        self.analysis_type_configurations = AnalysisTypeConfigurations(server=self)
        self.analysis_types = AnalysisTypes(server=self)
        self.api_tokens = ApiTokens(server=self)
        self.async_results = AsyncResults(server=self)
        self.chunked_files = ChunkedFiles(server=self)
        self.data_tables = DataTables(server=self)
        self.engagement_account_groupings = EngagementAccountGroupings(server=self)
        self.engagement_account_groups = EngagementAccountGroups(server=self)
        self.engagements = Engagements(server=self)
        self.file_infos = FileInfos(server=self)
        self.file_manager = FileManager(server=self)
        self.file_results = FileResults(server=self)
        self.json_tables = JSONTables(server=self)
        self.libraries = Libraries(server=self)
        self.organizations = Organizations(server=self)
        self.populations = Populations(server=self)
        self.risk_ranges = RiskRanges(server=self)
        self.task_histories = TaskHistories(server=self)
        self.tasks = Tasks(server=self)
        self.transaction_id_previews = TransactionIdPreviews(server=self)
        self.users = Users(server=self)
        self.webhooks = Webhooks(server=self)

        if logger.getEffectiveLevel() <= logging.DEBUG:
            logger.info("Enabling logging from http.client (for sent DEBUG info)")

            http.client.HTTPConnection.debuglevel = 1

            http.client.print = _print_to_log  # type: ignore[attr-defined]

    @cached_property
    def base_url(self) -> str:
        host = parse_url(self.url).host
        return Url(scheme="https", host=host, path="/api/v1").url
