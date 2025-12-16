from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import cast, Union
from typing import Union

if TYPE_CHECKING:
  from ..models.workspace_dto import WorkspaceDto





T = TypeVar("T", bound="SlimMiniDto")



@_attrs_define
class SlimMiniDto:
    """ 
        Attributes:
            id (Union[Unset, int]):
            name (Union[Unset, str]):
            description (Union[None, Unset, str]):
            instructions (Union[None, Unset, str]):
            template_id (Union[None, Unset, str]):
            workspaces (Union[Unset, list['WorkspaceDto']]):
     """

    id: Union[Unset, int] = UNSET
    name: Union[Unset, str] = UNSET
    description: Union[None, Unset, str] = UNSET
    instructions: Union[None, Unset, str] = UNSET
    template_id: Union[None, Unset, str] = UNSET
    workspaces: Union[Unset, list['WorkspaceDto']] = UNSET





    def to_dict(self) -> dict[str, Any]:
        from ..models.workspace_dto import WorkspaceDto
        id = self.id

        name = self.name

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        instructions: Union[None, Unset, str]
        if isinstance(self.instructions, Unset):
            instructions = UNSET
        else:
            instructions = self.instructions

        template_id: Union[None, Unset, str]
        if isinstance(self.template_id, Unset):
            template_id = UNSET
        else:
            template_id = self.template_id

        workspaces: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.workspaces, Unset):
            workspaces = []
            for workspaces_item_data in self.workspaces:
                workspaces_item = workspaces_item_data.to_dict()
                workspaces.append(workspaces_item)




        field_dict: dict[str, Any] = {}

        field_dict.update({
        })
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
        if instructions is not UNSET:
            field_dict["instructions"] = instructions
        if template_id is not UNSET:
            field_dict["templateId"] = template_id
        if workspaces is not UNSET:
            field_dict["workspaces"] = workspaces

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.workspace_dto import WorkspaceDto
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))


        def _parse_instructions(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        instructions = _parse_instructions(d.pop("instructions", UNSET))


        def _parse_template_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        template_id = _parse_template_id(d.pop("templateId", UNSET))


        workspaces = []
        _workspaces = d.pop("workspaces", UNSET)
        for workspaces_item_data in (_workspaces or []):
            workspaces_item = WorkspaceDto.from_dict(workspaces_item_data)



            workspaces.append(workspaces_item)


        slim_mini_dto = cls(
            id=id,
            name=name,
            description=description,
            instructions=instructions,
            template_id=template_id,
            workspaces=workspaces,
        )

        return slim_mini_dto

