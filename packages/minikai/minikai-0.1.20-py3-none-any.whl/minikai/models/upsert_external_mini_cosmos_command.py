from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast, Union
from typing import Union






T = TypeVar("T", bound="UpsertExternalMiniCosmosCommand")



@_attrs_define
class UpsertExternalMiniCosmosCommand:
    """ 
        Attributes:
            external_uri (Union[Unset, str]):
            name (Union[Unset, str]):
            profile_picture_url (Union[None, Unset, str]):
            profile (Union[Unset, Any]):
     """

    external_uri: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    profile_picture_url: Union[None, Unset, str] = UNSET
    profile: Union[Unset, Any] = UNSET





    def to_dict(self) -> dict[str, Any]:
        external_uri = self.external_uri

        name = self.name

        profile_picture_url: Union[None, Unset, str]
        if isinstance(self.profile_picture_url, Unset):
            profile_picture_url = UNSET
        else:
            profile_picture_url = self.profile_picture_url

        profile = self.profile


        field_dict: dict[str, Any] = {}

        field_dict.update({
        })
        if external_uri is not UNSET:
            field_dict["externalUri"] = external_uri
        if name is not UNSET:
            field_dict["name"] = name
        if profile_picture_url is not UNSET:
            field_dict["profilePictureUrl"] = profile_picture_url
        if profile is not UNSET:
            field_dict["profile"] = profile

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        external_uri = d.pop("externalUri", UNSET)

        name = d.pop("name", UNSET)

        def _parse_profile_picture_url(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        profile_picture_url = _parse_profile_picture_url(d.pop("profilePictureUrl", UNSET))


        profile = d.pop("profile", UNSET)

        upsert_external_mini_cosmos_command = cls(
            external_uri=external_uri,
            name=name,
            profile_picture_url=profile_picture_url,
            profile=profile,
        )

        return upsert_external_mini_cosmos_command

