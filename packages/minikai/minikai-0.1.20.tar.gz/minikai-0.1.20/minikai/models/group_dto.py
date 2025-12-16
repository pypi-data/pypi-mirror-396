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
  from ..models.slim_mini_dto import SlimMiniDto
  from ..models.user_dto import UserDto
  from ..models.mini_cosmos_dto import MiniCosmosDto





T = TypeVar("T", bound="GroupDto")



@_attrs_define
class GroupDto:
    """ 
        Attributes:
            id (Union[Unset, str]):
            name (Union[Unset, str]):
            description (Union[None, Unset, str]):
            workspace_id (Union[Unset, str]):
            users (Union[Unset, list['UserDto']]):
            minis (Union[Unset, list['SlimMiniDto']]):
            minis_cosmos (Union[Unset, list['MiniCosmosDto']]):
     """

    id: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    description: Union[None, Unset, str] = UNSET
    workspace_id: Union[Unset, str] = UNSET
    users: Union[Unset, list['UserDto']] = UNSET
    minis: Union[Unset, list['SlimMiniDto']] = UNSET
    minis_cosmos: Union[Unset, list['MiniCosmosDto']] = UNSET





    def to_dict(self) -> dict[str, Any]:
        from ..models.slim_mini_dto import SlimMiniDto
        from ..models.user_dto import UserDto
        from ..models.mini_cosmos_dto import MiniCosmosDto
        id = self.id

        name = self.name

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        workspace_id = self.workspace_id

        users: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.users, Unset):
            users = []
            for users_item_data in self.users:
                users_item = users_item_data.to_dict()
                users.append(users_item)



        minis: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.minis, Unset):
            minis = []
            for minis_item_data in self.minis:
                minis_item = minis_item_data.to_dict()
                minis.append(minis_item)



        minis_cosmos: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.minis_cosmos, Unset):
            minis_cosmos = []
            for minis_cosmos_item_data in self.minis_cosmos:
                minis_cosmos_item = minis_cosmos_item_data.to_dict()
                minis_cosmos.append(minis_cosmos_item)




        field_dict: dict[str, Any] = {}

        field_dict.update({
        })
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
        if workspace_id is not UNSET:
            field_dict["workspaceId"] = workspace_id
        if users is not UNSET:
            field_dict["users"] = users
        if minis is not UNSET:
            field_dict["minis"] = minis
        if minis_cosmos is not UNSET:
            field_dict["minisCosmos"] = minis_cosmos

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.slim_mini_dto import SlimMiniDto
        from ..models.user_dto import UserDto
        from ..models.mini_cosmos_dto import MiniCosmosDto
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


        workspace_id = d.pop("workspaceId", UNSET)

        users = []
        _users = d.pop("users", UNSET)
        for users_item_data in (_users or []):
            users_item = UserDto.from_dict(users_item_data)



            users.append(users_item)


        minis = []
        _minis = d.pop("minis", UNSET)
        for minis_item_data in (_minis or []):
            minis_item = SlimMiniDto.from_dict(minis_item_data)



            minis.append(minis_item)


        minis_cosmos = []
        _minis_cosmos = d.pop("minisCosmos", UNSET)
        for minis_cosmos_item_data in (_minis_cosmos or []):
            minis_cosmos_item = MiniCosmosDto.from_dict(minis_cosmos_item_data)



            minis_cosmos.append(minis_cosmos_item)


        group_dto = cls(
            id=id,
            name=name,
            description=description,
            workspace_id=workspace_id,
            users=users,
            minis=minis,
            minis_cosmos=minis_cosmos,
        )

        return group_dto

