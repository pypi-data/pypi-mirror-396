from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset







T = TypeVar("T", bound="PostPublicEnvelopeCreateResponse200PresignedS3ParamsFields")



@_attrs_define
class PostPublicEnvelopeCreateResponse200PresignedS3ParamsFields:
    """ Fields required for the upload.

        Attributes:
            bucket (str): The bucket name.
            key (str): The object key.
            content_type (str): The content type.
            x_amz_algorithm (str): The algorithm.
            x_amz_credential (str): The credential.
            x_amz_date (str): The date.
            policy (str): The policy.
            x_amz_signature (str): The signature.
     """

    bucket: str
    key: str
    content_type: str
    x_amz_algorithm: str
    x_amz_credential: str
    x_amz_date: str
    policy: str
    x_amz_signature: str





    def to_dict(self) -> dict[str, Any]:
        bucket = self.bucket

        key = self.key

        content_type = self.content_type

        x_amz_algorithm = self.x_amz_algorithm

        x_amz_credential = self.x_amz_credential

        x_amz_date = self.x_amz_date

        policy = self.policy

        x_amz_signature = self.x_amz_signature


        field_dict: dict[str, Any] = {}

        field_dict.update({
            "bucket": bucket,
            "key": key,
            "content-type": content_type,
            "x-amz-algorithm": x_amz_algorithm,
            "x-amz-credential": x_amz_credential,
            "x-amz-date": x_amz_date,
            "policy": policy,
            "x-amz-signature": x_amz_signature,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        bucket = d.pop("bucket")

        key = d.pop("key")

        content_type = d.pop("content-type")

        x_amz_algorithm = d.pop("x-amz-algorithm")

        x_amz_credential = d.pop("x-amz-credential")

        x_amz_date = d.pop("x-amz-date")

        policy = d.pop("policy")

        x_amz_signature = d.pop("x-amz-signature")

        post_public_envelope_create_response_200_presigned_s3_params_fields = cls(
            bucket=bucket,
            key=key,
            content_type=content_type,
            x_amz_algorithm=x_amz_algorithm,
            x_amz_credential=x_amz_credential,
            x_amz_date=x_amz_date,
            policy=policy,
            x_amz_signature=x_amz_signature,
        )

        return post_public_envelope_create_response_200_presigned_s3_params_fields

