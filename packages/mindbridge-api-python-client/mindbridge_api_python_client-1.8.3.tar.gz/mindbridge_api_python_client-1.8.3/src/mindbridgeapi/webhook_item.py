#
#  Copyright MindBridge Analytics Inc. all rights reserved.
#
#  This material is confidential and may not be copied, distributed,
#  reversed engineered, decompiled or otherwise disseminated without
#  the prior written consent of MindBridge Analytics Inc.
#

from typing import Any
from pydantic import ConfigDict, model_validator
from mindbridgeapi.common_validators import _warning_if_extra_fields
from mindbridgeapi.generated_pydantic_model.model import (
    ApiWebhookCreate,
    ApiWebhookRead,
    ApiWebhookUpdate,
    Event as _WebhookEvent,
    Status10 as _WebhookStatus,
)

WebhookEvent = _WebhookEvent
WebhookStatus = _WebhookStatus


class WebhookItem(ApiWebhookRead):
    """Represents a specific Webhook.

    ```py
    import os
    import mindbridgeapi as mbapi

    server = mbapi.Server(
        url=os.environ["MINDBRIDGE_API_TEST_URL"],
        token=os.environ["MINDBRIDGE_API_TEST_TOKEN"],
    )
    user = next(server.users.get({"role": mbapi.UserRole.ROLE_ADMIN}))
    webhook = mbapi.WebhookItem(
        url=webhook_url,
        events=[mbapi.WebhookEvent.ENGAGEMENT_CREATED],
        status=mbapi.WebhookStatus.ACTIVE,
        name="webhook_952679e5683948dcb2892af7e75d9b21",
        technical_contact_id=user.id,
    )
    ```

    Attributes:
        id (str): The unique object identifier.
        url (str): The URL to which the webhook will send notifications.
        name (str): The name of the webhook.
        technical_contact_id (str): A reference to an administrative user used to inform
            system administrators of issues with the webhooks.
        events (list[WebhookEvent]): A list of events that will trigger this webhook.
        status (WebhookStatus): The current status of the webhook.
        public_key (str): The public key used to verify the webhook signature.
    """

    model_config = ConfigDict(
        extra="allow",
        validate_assignment=True,
        validate_default=True,
        validate_return=True,
    )
    _ = model_validator(mode="after")(_warning_if_extra_fields)

    def _get_post_json(
        self, out_class: type[ApiWebhookCreate | ApiWebhookUpdate]
    ) -> dict[str, Any]:
        in_class_dict = self.model_dump()
        out_class_object = out_class.model_validate(in_class_dict)
        return out_class_object.model_dump(
            mode="json", by_alias=True, exclude_none=True
        )

    @property
    def create_json(self) -> dict[str, Any]:
        return self._get_post_json(out_class=ApiWebhookCreate)

    @property
    def update_json(self) -> dict[str, Any]:
        return self._get_post_json(out_class=ApiWebhookUpdate)
