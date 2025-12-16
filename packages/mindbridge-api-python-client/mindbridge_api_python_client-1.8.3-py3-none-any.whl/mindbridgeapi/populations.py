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
from mindbridgeapi.population_item import PopulationItem

if TYPE_CHECKING:
    from collections.abc import Generator


@dataclass
class Populations(BaseSet):
    """Use to interact with Populations.

    Typical usage of these functions would be accessed from the server, for example:
    ```py
    from datetime import date
    import os
    import mindbridgeapi as mbapi

    server = mbapi.Server(
        url=os.environ["MINDBRIDGE_API_TEST_URL"],
        token=os.environ["MINDBRIDGE_API_TEST_TOKEN"],
    )
    analysis_result = next(server.analysis_results.get())
    item = mbapi.PopulationItem(
        name="a_population_name",
        analysis_type_id=analysis_result.analysis_type_id,
        category="a_population_category",
        condition=mbapi.FilterGroupConditionItem(
            operator="AND",
            conditions=[
                mbapi.FilterAccountConditionItem(
                    account_selections=[
                        mbapi.FilterAccountSelectionItem(
                            use_account_id=False, code="1000", name="Assets"
                        )
                    ],
                    field="account_hierarchy_codes",
                ),
                mbapi.FilterDateValueSpecificValueConditionItem(
                    field="effective_date", value=date(2000, 1, 1)
                ),
            ],
        ),
        analysis_id=analysis_result.analysis_id,
    )
    item = server.populations.create(item)
    print(f"Created {item.name}")
    ```
    """

    @cached_property
    def base_url(self) -> str:
        return f"{self.server.base_url}/populations"

    def create(self, population_item: PopulationItem) -> PopulationItem:
        """Creates a new Population on the server.

        Args:
            population_item (PopulationItem): The Population to create.

        Returns:
            (PopulationItem): The created Population.

        Raises:
            ItemAlreadyExistsError: If the population_item already has an ID.
        """
        population_item = PopulationItem.model_validate(population_item)

        if population_item.id:
            raise ItemAlreadyExistsError(population_item.id)

        resp_dict = super()._create(url=self.base_url, json=population_item.create_json)
        return PopulationItem.model_validate(resp_dict)

    def delete(self, population_item: PopulationItem) -> None:
        """Deletes a Population from the server.

        Args:
            population_item (PopulationItem): The Population to delete.

        Raises:
            ItemNotFoundError: If the population_item does not have an ID.
        """
        population_item = PopulationItem.model_validate(population_item)

        if not population_item.id:
            raise ItemNotFoundError

        super()._delete(url=f"{self.base_url}/{population_item.id}")

    def get(
        self, json: dict[str, Any] | None = None
    ) -> "Generator[PopulationItem, None, None]":
        """Retrieves Populations from the server based on the provided query parameters.

        Args:
            json (Optional[dict[str, Any]]): Query parameters for filtering Populations.

        Yields:
            (PopulationItem): The next Population from the generator.
        """
        if json is None:
            json = {}

        for resp_dict in super()._get(url=f"{self.base_url}/query", json=json):
            yield PopulationItem.model_validate(resp_dict)

    def get_by_id(self, id: str) -> PopulationItem:
        """Retrieves a Population by its ID from the server.

        Args:
            id (str): The ID of the Population to retrieve.

        Returns:
            (PopulationItem): The Population with the specified ID.
        """
        resp_dict = super()._get_by_id(url=f"{self.base_url}/{id}")

        return PopulationItem.model_validate(resp_dict)

    def update(self, population_item: PopulationItem) -> PopulationItem:
        """Updates an existing Population on the server.

        Args:
            population_item (PopulationItem): The Population to update.

        Returns:
            (PopulationItem): The updated Population.

        Raises:
            ItemNotFoundError: If the population_item does not have an ID.
        """
        population_item = PopulationItem.model_validate(population_item)

        if not population_item.id:
            raise ItemNotFoundError

        resp_dict = super()._update(
            url=f"{self.base_url}/{population_item.id}",
            json=population_item.update_json,
        )

        return PopulationItem.model_validate(resp_dict)
