from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.workspace_type import check_workspace_type
from ..models.workspace_type import WorkspaceType
from ..types import UNSET, Unset
from typing import cast
from typing import cast, Union
from typing import Union






T = TypeVar("T", bound="WorkspaceDto")



@_attrs_define
class WorkspaceDto:
    """ 
        Attributes:
            id (Union[Unset, int]):
            workspace_id (Union[Unset, str]):
            name (Union[Unset, str]):
            organization_id (Union[None, Unset, str]):
            workspace_type (Union[None, Unset, WorkspaceType]):
     """

    id: Union[Unset, int] = UNSET
    workspace_id: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    organization_id: Union[None, Unset, str] = UNSET
    workspace_type: Union[None, Unset, WorkspaceType] = UNSET





    def to_dict(self) -> dict[str, Any]:
        id = self.id

        workspace_id = self.workspace_id

        name = self.name

        organization_id: Union[None, Unset, str]
        if isinstance(self.organization_id, Unset):
            organization_id = UNSET
        else:
            organization_id = self.organization_id

        workspace_type: Union[None, Unset, str]
        if isinstance(self.workspace_type, Unset):
            workspace_type = UNSET
        elif isinstance(self.workspace_type, str):
            workspace_type = self.workspace_type
        else:
            workspace_type = self.workspace_type


        field_dict: dict[str, Any] = {}

        field_dict.update({
        })
        if id is not UNSET:
            field_dict["id"] = id
        if workspace_id is not UNSET:
            field_dict["workspaceId"] = workspace_id
        if name is not UNSET:
            field_dict["name"] = name
        if organization_id is not UNSET:
            field_dict["organizationId"] = organization_id
        if workspace_type is not UNSET:
            field_dict["workspaceType"] = workspace_type

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        workspace_id = d.pop("workspaceId", UNSET)

        name = d.pop("name", UNSET)

        def _parse_organization_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        organization_id = _parse_organization_id(d.pop("organizationId", UNSET))


        def _parse_workspace_type(data: object) -> Union[None, Unset, WorkspaceType]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                workspace_type_type_0 = check_workspace_type(data)



                return workspace_type_type_0
            except: # noqa: E722
                pass
            return cast(Union[None, Unset, WorkspaceType], data)

        workspace_type = _parse_workspace_type(d.pop("workspaceType", UNSET))


        workspace_dto = cls(
            id=id,
            workspace_id=workspace_id,
            name=name,
            organization_id=organization_id,
            workspace_type=workspace_type,
        )

        return workspace_dto

