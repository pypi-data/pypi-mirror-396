#
#  Copyright MindBridge Analytics Inc. all rights reserved.
#
#  This material is confidential and may not be copied, distributed,
#  reversed engineered, decompiled or otherwise disseminated without
#  the prior written consent of MindBridge Analytics Inc.
#

import logging
from typing import Any
import warnings
from pydantic import RootModel
from mindbridgeapi.exceptions import ParameterError
from mindbridgeapi.generated_pydantic_model.model import (
    ApiUserInfo,
    ApiUserInfoRead,
    ApiUserRead as UserItem,
    Role,
)

MindBridgeQuery = RootModel[dict[str, Any]]

logger = logging.getLogger(__name__)


def _warning_if_extra_fields(self: Any) -> Any:
    """Emits a warning if the model had any extra fields.

    This is used to create a warning if and only if the model had any extra fields, but
    still allow the model to be used. For example:
    ```py
    x = mbapi.AccountingPeriod(badkey="ksodhjksdl")
    AccountingPeriod had extra fields, specifically:
                  badkey: ksodhjksdl
    ```

    Returns:
        Any: The original object
    """
    if self.model_extra is None or len(self.model_extra) == 0:
        return self

    log_lines = [f"{type(self).__name__} had extra fields, specifically:"]
    for key, value in self.model_extra.items():
        log_lines.append(f"{key.rjust(20)}: {value}")

    warn_message = "\n".join(log_lines)
    warnings.warn(warn_message, stacklevel=2)

    return self


def _convert_userinfo_to_useritem(v: Any) -> Any:
    """Converts from UserInfo to UserItem.

    If it's a ApiUserInfo or ApiUserInfoRead it changes to UserItem, with just the
    relevant fields set. It also does some extra conversion if it seems to be an API
    user.

    Args:
        v (Any): The original data

    Returns:
        Any: UserItem if possible, the original data otherwise
    """
    if not isinstance(v, (ApiUserInfo, ApiUserInfoRead)):
        return v

    prefix = "(API) "
    if v.user_name is None or not v.user_name.startswith(prefix):
        return UserItem(id=v.user_id, first_name=v.user_name)

    prefix_len = len(prefix)
    first_name = v.user_name[prefix_len:]
    return UserItem(
        id=v.user_id, first_name=first_name, last_name="", role=Role.ROLE_ADMIN
    )


def _convert_json_query(
    json: dict[str, Any] | None, required_key: str | None = None
) -> dict[str, int | float | bool | str]:
    if json is None:
        json = {}

    mb_query = MindBridgeQuery.model_validate(json)
    json_str = mb_query.model_dump_json(exclude_none=True)

    logger.info("Query (get) is: %s", json_str)

    if required_key is not None and required_key not in json_str:
        raise ParameterError(
            parameter_name="json",
            details=(
                f"At least one valid {required_key} term must be provided when querying"
                " this entity."
            ),
        )

    mb_query_dict: dict[str, int | float | bool | str] = mb_query.model_dump(
        mode="json", exclude_none=True
    )
    return mb_query_dict
