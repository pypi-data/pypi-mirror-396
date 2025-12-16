#
#  Copyright MindBridge Analytics Inc. all rights reserved.
#
#  This material is confidential and may not be copied, distributed,
#  reversed engineered, decompiled or otherwise disseminated without
#  the prior written consent of MindBridge Analytics Inc.
#

from typing import ClassVar
from pydantic import ConfigDict, field_validator, model_validator
from mindbridgeapi.common_validators import (
    _convert_userinfo_to_useritem,
    _warning_if_extra_fields,
)
from mindbridgeapi.generated_pydantic_model.model import ApiAnalysisSourceTypeRead


class AnalysisSourceTypeItem(ApiAnalysisSourceTypeRead):
    GENERAL_LEDGER_JOURNAL: ClassVar[str] = "4b8361d00000000000000000"
    OPENING_BALANCE: ClassVar[str] = "4b8361d00000000000000002"
    CLOSING_BALANCE: ClassVar[str] = "4b8361d00000000000000003"
    CHART_OF_ACCOUNTS: ClassVar[str] = "4b8361d00000000000000004"
    ADJUSTING_ENTRIES: ClassVar[str] = "4b8361d00000000000000016"
    RECLASSIFICATION_ENTRIES: ClassVar[str] = "4b8361d00000000000000017"
    ELIMINATION_ENTRIES: ClassVar[str] = "4b8361d00000000000000018"
    NOT_FOR_PROFIT_GENERAL_LEDGER_JOURNAL: ClassVar[str] = "4b8361d00000000000000051"
    NOT_FOR_PROFIT_OPENING_BALANCE: ClassVar[str] = "4b8361d00000000000000057"
    NOT_FOR_PROFIT_CLOSING_BALANCE: ClassVar[str] = "4b8361d00000000000000058"
    GENERAL_LEDGER_JOURNAL_FUND: ClassVar[str] = "4b8361d00000000000000001"
    FUND_OPENING_BALANCE: ClassVar[str] = "4b8361d00000000000000059"
    FUND_CLOSING_BALANCE: ClassVar[str] = "4b8361d0000000000000005a"
    FUND_CHART_OF_ACCOUNTS: ClassVar[str] = "4b8361d00000000000000005"
    ACCOUNTS_PAYABLE_DETAIL: ClassVar[str] = "4b8361d00000000000000006"
    CLOSING_PAYABLES_LIST: ClassVar[str] = "4b8361d00000000000000010"
    VENDOR_OPENING_BALANCES: ClassVar[str] = "4b8361d00000000000000007"
    VENDOR_LIST: ClassVar[str] = "4b8361d00000000000000008"
    OPEN_PAYABLES_LIST: ClassVar[str] = "4b8361d00000000000000009"
    ACCOUNTS_RECEIVABLE_DETAIL: ClassVar[str] = "4b8361d00000000000000011"
    CLOSING_RECEIVABLES_LIST: ClassVar[str] = "4b8361d00000000000000014"
    CUSTOMER_OPENING_BALANCES: ClassVar[str] = "4b8361d00000000000000012"
    CUSTOMER_LIST: ClassVar[str] = "4b8361d00000000000000039"
    OPEN_RECEIVABLES_LIST: ClassVar[str] = "4b8361d00000000000000013"
    ADDITIONAL_ANALYSIS_DATA: ClassVar[str] = "4b8361d00000000000000015"
    FUND_ADJUSTING_ENTRIES: ClassVar[str] = "4b8361d00000000000000019"
    FUND_ELIMINATION_ENTRIES: ClassVar[str] = "4b8361d00000000000000020"
    FUND_RECLASSIFICATION_ENTRIES: ClassVar[str] = "4b8361d00000000000000021"

    model_config = ConfigDict(
        extra="allow",
        validate_assignment=True,
        validate_default=True,
        validate_return=True,
    )
    _a = model_validator(mode="after")(_warning_if_extra_fields)
    _b = field_validator("*")(_convert_userinfo_to_useritem)
