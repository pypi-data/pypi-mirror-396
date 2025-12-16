from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import Union






T = TypeVar("T", bound="MiniGroupSummaryDto")



@_attrs_define
class MiniGroupSummaryDto:
    """ 
        Attributes:
            id (Union[Unset, str]):
            name (Union[Unset, str]):
            mini_count (Union[Unset, int]):
            user_count (Union[Unset, int]):
     """

    id: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    mini_count: Union[Unset, int] = UNSET
    user_count: Union[Unset, int] = UNSET





    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        mini_count = self.mini_count

        user_count = self.user_count


        field_dict: dict[str, Any] = {}

        field_dict.update({
        })
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if mini_count is not UNSET:
            field_dict["miniCount"] = mini_count
        if user_count is not UNSET:
            field_dict["userCount"] = user_count

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        name = d.pop("name", UNSET)

        mini_count = d.pop("miniCount", UNSET)

        user_count = d.pop("userCount", UNSET)

        mini_group_summary_dto = cls(
            id=id,
            name=name,
            mini_count=mini_count,
            user_count=user_count,
        )

        return mini_group_summary_dto

