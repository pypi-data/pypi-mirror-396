#
#  Copyright MindBridge Analytics Inc. all rights reserved.
#
#  This material is confidential and may not be copied, distributed,
#  reversed engineered, decompiled or otherwise disseminated without
#  the prior written consent of MindBridge Analytics Inc.
#

from typing import Annotated, Any
from pydantic import ConfigDict, Field, computed_field, field_validator, model_validator
from mindbridgeapi.common_validators import (
    _convert_userinfo_to_useritem,
    _warning_if_extra_fields,
)
from mindbridgeapi.generated_pydantic_model.model import (
    ApiFileManagerDirectoryCreate,
    ApiFileManagerDirectoryUpdate,
    ApiFileManagerFileCreate,
    ApiFileManagerFileRead,
    ApiFileManagerFileUpdate,
    Type9 as _FileManagerType,
)

FileManagerType = _FileManagerType  # Match the type of FileManagerItem.type
_get_post_json_out_class_type = type[
    ApiFileManagerDirectoryCreate
    | ApiFileManagerDirectoryUpdate
    | ApiFileManagerFileCreate
    | ApiFileManagerFileUpdate
]


class FileManagerItem(ApiFileManagerFileRead):
    """A File or Directory on the File manager."""

    engagement_id: Annotated[
        str | None,
        Field(
            alias=ApiFileManagerFileRead.model_fields["engagement_id"].alias,
            description=ApiFileManagerFileRead.model_fields[
                "engagement_id"
            ].description,
        ),
    ] = None  # type: ignore[assignment]
    version: Annotated[
        int | None,
        Field(description=ApiFileManagerFileRead.model_fields["version"].description),
    ] = None  # type: ignore[assignment]

    model_config = ConfigDict(
        extra="allow",
        validate_assignment=True,
        validate_default=True,
        validate_return=True,
    )
    _a = model_validator(mode="after")(_warning_if_extra_fields)
    _b = field_validator("*")(_convert_userinfo_to_useritem)

    def _get_post_json(
        self, out_class: _get_post_json_out_class_type
    ) -> dict[str, Any]:
        in_class_dict = self.model_dump()
        out_class_object = out_class.model_validate(in_class_dict)
        return out_class_object.model_dump(
            mode="json", by_alias=True, exclude_none=True
        )

    @property
    def create_json(self) -> dict[str, Any]:
        return self._get_post_json(ApiFileManagerDirectoryCreate)

    @property
    def create_body(self) -> str:
        in_class_dict = self.model_dump()
        out_class_object = ApiFileManagerFileCreate.model_validate(in_class_dict)
        return out_class_object.model_dump_json(by_alias=True, exclude_none=True)

    @property
    def update_json(self) -> dict[str, Any]:
        if self.type == FileManagerType.FILE:
            return self._get_post_json(ApiFileManagerFileUpdate)

        # type must be FileManagerType.DIRECTORY
        return self._get_post_json(ApiFileManagerDirectoryUpdate)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def filename(self) -> str:
        str_name = self.name or ""
        str_extension = self.extension or ""

        if str_extension:
            return f"{str_name}.{str_extension}"

        return str_name
