from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field
import json
from .. import types

from ..types import UNSET, Unset







T = TypeVar("T", bound="PostPublicEnvelopeCreateFromFileBody")



@_attrs_define
class PostPublicEnvelopeCreateFromFileBody:
    """ 
        Attributes:
            workspace_uuid (str): The UUID of the workspace to create the envelope in.
            envelope_title (str): The title of the envelope being created.
            file (Any): The file to upload (PDF or Word document, max 50MB).
     """

    workspace_uuid: str
    envelope_title: str
    file: Any
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        workspace_uuid = self.workspace_uuid

        envelope_title = self.envelope_title

        file = self.file


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "workspaceUuid": workspace_uuid,
            "envelopeTitle": envelope_title,
            "file": file,
        })

        return field_dict


    def to_multipart(self) -> types.RequestFiles:
        files: types.RequestFiles = []

        files.append(("workspaceUuid", (None, str(self.workspace_uuid).encode(), "text/plain")))



        files.append(("envelopeTitle", (None, str(self.envelope_title).encode(), "text/plain")))



        files.append(("file", (None, str(self.file).encode(), "text/plain")))




        for prop_name, prop in self.additional_properties.items():
            files.append((prop_name, (None, str(prop).encode(), "text/plain")))



        return files


    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        workspace_uuid = d.pop("workspaceUuid")

        envelope_title = d.pop("envelopeTitle")

        file = d.pop("file")

        post_public_envelope_create_from_file_body = cls(
            workspace_uuid=workspace_uuid,
            envelope_title=envelope_title,
            file=file,
        )


        post_public_envelope_create_from_file_body.additional_properties = d
        return post_public_envelope_create_from_file_body

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
