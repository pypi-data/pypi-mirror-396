from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from typing import cast, Union
from typing import Union
import datetime






T = TypeVar("T", bound="MiniCosmosDto")



@_attrs_define
class MiniCosmosDto:
    """ 
        Attributes:
            id (Union[Unset, str]):
            name (Union[Unset, str]):
            profile_picture_url (Union[None, Unset, str]):
            profile (Union[Unset, Any]):
            external_uri (Union[None, Unset, str]):
            created_at (Union[Unset, datetime.datetime]):
            created_by (Union[Unset, str]):
            updated_at (Union[Unset, datetime.datetime]):
            updated_by (Union[None, Unset, str]):
     """

    id: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    profile_picture_url: Union[None, Unset, str] = UNSET
    profile: Union[Unset, Any] = UNSET
    external_uri: Union[None, Unset, str] = UNSET
    created_at: Union[Unset, datetime.datetime] = UNSET
    created_by: Union[Unset, str] = UNSET
    updated_at: Union[Unset, datetime.datetime] = UNSET
    updated_by: Union[None, Unset, str] = UNSET





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

        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        created_by = self.created_by

        updated_at: Union[Unset, str] = UNSET
        if not isinstance(self.updated_at, Unset):
            updated_at = self.updated_at.isoformat()

        updated_by: Union[None, Unset, str]
        if isinstance(self.updated_by, Unset):
            updated_by = UNSET
        else:
            updated_by = self.updated_by


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
        if created_at is not UNSET:
            field_dict["createdAt"] = created_at
        if created_by is not UNSET:
            field_dict["createdBy"] = created_by
        if updated_at is not UNSET:
            field_dict["updatedAt"] = updated_at
        if updated_by is not UNSET:
            field_dict["updatedBy"] = updated_by

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


        _created_at = d.pop("createdAt", UNSET)
        created_at: Union[Unset, datetime.datetime]
        if isinstance(_created_at,  Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)




        created_by = d.pop("createdBy", UNSET)

        _updated_at = d.pop("updatedAt", UNSET)
        updated_at: Union[Unset, datetime.datetime]
        if isinstance(_updated_at,  Unset):
            updated_at = UNSET
        else:
            updated_at = isoparse(_updated_at)




        def _parse_updated_by(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        updated_by = _parse_updated_by(d.pop("updatedBy", UNSET))


        mini_cosmos_dto = cls(
            id=id,
            name=name,
            profile_picture_url=profile_picture_url,
            profile=profile,
            external_uri=external_uri,
            created_at=created_at,
            created_by=created_by,
            updated_at=updated_at,
            updated_by=updated_by,
        )

        return mini_cosmos_dto

