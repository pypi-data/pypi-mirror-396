#
#  Copyright MindBridge Analytics Inc. all rights reserved.
#
#  This material is confidential and may not be copied, distributed,
#  reversed engineered, decompiled or otherwise disseminated without
#  the prior written consent of MindBridge Analytics Inc.
#
from mindbridgeapi.version import VERSION


class MBAPIError(Exception):
    """Base exception used by this module."""

    def __init__(self, details: str) -> None:
        self.details = details
        super().__init__(
            f"{details} For reference your MindBridge API Python Client version is: "
            f"{VERSION}."
        )


class ParameterError(MBAPIError):
    """The function call had an unexpected parameter error.

    This is a general exception for a parameter had an unexpected value for the function
    requested. ItemError would be used if it was an issue with a Item.
    """

    def __init__(self, parameter_name: str, details: str) -> None:
        self.details = details
        super().__init__(
            f"The {parameter_name} parameter was an unexpected value. Specifically: "
            f"{details}"
        )


class ItemError(MBAPIError):
    """The item had unexpected attributes.

    This is a general exception for the item had unexpected attributes for the function
    requested. There may be more specific exceptions available.
    """

    def __init__(self, details: str) -> None:
        self.details = details
        super().__init__(f"Item had an unexpected attributes. Specifically: {details}")


class ItemAlreadyExistsError(ItemError):
    """The item had an id when it shouldn't have for the action wanted.

    When creating an item on the server, the id must be None as otherwise it means that
    the item has already been created on the server.
    """

    def __init__(self, id: str) -> None:
        self.id = id
        super().__init__(
            f"Item has an id of {id}, which implies it has already been created on the "
            "server."
        )


class ItemNotFoundError(ItemError):
    """The item had no id when it should have for the action wanted.

    When updating, deleting or some other actions the item must already exist on the
    server which means the id must not be None.
    """

    def __init__(self) -> None:
        super().__init__(
            "Item has no id, which implies it does not exist on the server."
        )


class UnexpectedServerError(MBAPIError):
    """MindBridge returned something we didn't expect.

    This represents a MindBridge error that shouldn't have occurred.
    """

    def __init__(self, details: str) -> None:
        self.details = details
        super().__init__(
            f"MindBridge provided an unexpected response. Specifically: {details}"
        )


class ValidationError(MBAPIError):
    """MindBridge found an error.

    The request was likely valid, but MindBridge determined an issue with the data. For
    example, when creating an organization MindBridge found that there was already an
    organization with the same name on the server.
    """

    def __init__(self, details: str) -> None:
        self.details = details
        super().__init__(f"MindBridge found an issue: {details}")
