#
#  Copyright MindBridge Analytics Inc. all rights reserved.
#
#  This material is confidential and may not be copied, distributed,
#  reversed engineered, decompiled or otherwise disseminated without
#  the prior written consent of MindBridge Analytics Inc.
#

from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING, Any
from mindbridgeapi.base_set import BaseSet
from mindbridgeapi.exceptions import ItemAlreadyExistsError, ItemNotFoundError
from mindbridgeapi.risk_ranges_item import RiskRangesItem

if TYPE_CHECKING:
    from collections.abc import Generator


@dataclass
class RiskRanges(BaseSet):
    """Use to interact with Risk Ranges.

    Typical usage of these functions would be accessed from the server, for example:
    ```py
    import os
    import uuid
    import mindbridgeapi as mbapi

    server = mbapi.Server(
        url=os.environ["MINDBRIDGE_API_TEST_URL"],
        token=os.environ["MINDBRIDGE_API_TEST_TOKEN"],
    )
    library = next(x for x in server.libraries.get() if not x.system)
    item = mbapi.RiskRangesItem(
        name=f"risk_range_{uuid.uuid4().hex}",
        library_id=library.id,
        analysis_type_id=library.analysis_type_ids[0],
        low=mbapi.RiskRangeBounds(low_threshold=0, high_threshold=50_00),
        high=mbapi.RiskRangeBounds(low_threshold=50_01, high_threshold=100_00),
    )
    token = server.risk_ranges.create(item)
    print(f"Created {item.name!r}")
    ```
    """

    @cached_property
    def base_url(self) -> str:
        return f"{self.server.base_url}/risk-ranges"

    def create(self, risk_ranges_item: RiskRangesItem) -> RiskRangesItem:
        """Creates a new Risk Ranges on the server.

        Args:
            risk_ranges_item (RiskRangesItem): The Risk Ranges item to create.

        Returns:
            (RiskRangesItem): The created Risk Ranges item.

        Raises:
            ItemAlreadyExistsError: If the risk_ranges_item already has an ID.
        """
        risk_ranges_item = RiskRangesItem.model_validate(risk_ranges_item)
        if risk_ranges_item.id:
            raise ItemAlreadyExistsError(risk_ranges_item.id)

        resp_dict = super()._create(
            url=self.base_url, json=risk_ranges_item.create_json
        )
        return RiskRangesItem.model_validate(resp_dict)

    def delete(self, risk_ranges_item: RiskRangesItem) -> None:
        """Deletes a Risk Ranges from the server.

        Args:
            risk_ranges_item (RiskRangesItem): The Risk Ranges item to delete.

        Raises:
            ItemNotFoundError: If the risk_ranges_item does not have an ID.
        """
        risk_ranges_item = RiskRangesItem.model_validate(risk_ranges_item)

        if not risk_ranges_item.id:
            raise ItemNotFoundError

        super()._delete(url=f"{self.base_url}/{risk_ranges_item.id}")

    def get(
        self, json: dict[str, Any] | None = None
    ) -> "Generator[RiskRangesItem, None, None]":
        """Retrieves Risk Ranges from the server based on the provided query parameters.

        Args:
            json (Optional[dict[str, Any]]): Query parameters for filtering Risk Ranges.

        Yields:
            (RiskRangesItem): A generator of Risk Ranges items.
        """
        if json is None:
            json = {}

        for resp_dict in super()._get(url=f"{self.base_url}/query", json=json):
            yield RiskRangesItem.model_validate(resp_dict)

    def get_by_id(self, id: str) -> RiskRangesItem:
        """Retrieves a Risk Ranges by its ID from the server.

        Args:
            id (str): The ID of the Risk Ranges to retrieve.

        Returns:
            (RiskRangesItem): The Risk Ranges item with the specified ID.
        """
        resp_dict = super()._get_by_id(url=f"{self.base_url}/{id}")
        return RiskRangesItem.model_validate(resp_dict)

    def update(self, risk_ranges_item: RiskRangesItem) -> RiskRangesItem:
        """Updates an existing Risk Ranges on the server.

        Args:
            risk_ranges_item (RiskRangesItem): The Risk Ranges item to update.

        Returns:
            (RiskRangesItem): The updated Risk Ranges item.

        Raises:
            ItemNotFoundError: If the risk_ranges_item does not have an ID.
        """
        risk_ranges_item = RiskRangesItem.model_validate(risk_ranges_item)

        if not risk_ranges_item.id:
            raise ItemNotFoundError

        resp_dict = super()._update(
            url=f"{self.base_url}/{risk_ranges_item.id}",
            json=risk_ranges_item.update_json,
        )

        return RiskRangesItem.model_validate(resp_dict)
