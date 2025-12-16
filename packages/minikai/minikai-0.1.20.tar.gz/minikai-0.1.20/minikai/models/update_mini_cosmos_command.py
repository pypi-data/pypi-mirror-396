from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast, Union
from typing import Union






T = TypeVar("T", bound="UpdateMiniCosmosCommand")



@_attrs_define
class UpdateMiniCosmosCommand:
    """ 
        Attributes:
            id (Union[Unset, str]):
            name (Union[Unset, str]):
            profile_picture_url (Union[None, Unset, str]):
            profile (Union[Unset, Any]):
            external_uri (Union[None, Unset, str]):
     """

    id: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    profile_picture_url: Union[None, Unset, str] = UNSET
    profile: Union[Unset, Any] = UNSET
    external_uri: Union[None, Unset, str] = UNSET





    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        profile_picture_url: Union[None, Unset, str]
        if isinstance(self.profile_picture_url, Unset):
            profile_picture_url = UNSET
        else:
            profile_picture_url = self.profile_picture_url

        profile = self.profile

        external_uri: Union[None, Unset, str]
        if isinstance(self.external_uri, Unset):
            external_uri = UNSET
        else:
            external_uri = self.external_uri


        field_dict: dict[str, Any] = {}

        field_dict.update({
        })
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if profile_picture_url is not UNSET:
            field_dict["profilePictureUrl"] = profile_picture_url
        if profile is not UNSET:
            field_dict["profile"] = profile
        if external_uri is not UNSET:
            field_dict["externalUri"] = external_uri

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        def _parse_profile_picture_url(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        profile_picture_url = _parse_profile_picture_url(d.pop("profilePictureUrl", UNSET))


        profile = d.pop("profile", UNSET)

        def _parse_external_uri(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        external_uri = _parse_external_uri(d.pop("externalUri", UNSET))


        update_mini_cosmos_command = cls(
            id=id,
            name=name,
            profile_picture_url=profile_picture_url,
            profile=profile,
            external_uri=external_uri,
        )

        return update_mini_cosmos_command

