#
#  Copyright MindBridge Analytics Inc. all rights reserved.
#
#  This material is confidential and may not be copied, distributed,
#  reversed engineered, decompiled or otherwise disseminated without
#  the prior written consent of MindBridge Analytics Inc.
#
from typing import cast

VERSION = "1.8.3"


def get_package_name() -> str:
    return "mindbridge-api-python-client"


def get_version() -> str:
    return VERSION


def get_version_tuple() -> tuple[int, int, int]:
    version_list_str = VERSION.split(".")
    expected_version_list_len = 3
    if len(version_list_str) != expected_version_list_len or not all(
        x.isdigit() for x in version_list_str
    ):
        msg = f"Unexpected version for {get_package_name()!r}: {VERSION!r}"
        raise ValueError(msg)

    return cast("tuple[int, int, int]", tuple(int(x) for x in version_list_str))
