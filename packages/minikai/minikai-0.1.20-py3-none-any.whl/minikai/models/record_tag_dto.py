from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import Union






T = TypeVar("T", bound="RecordTagDto")



@_attrs_define
class RecordTagDto:
    """ 
        Attributes:
            key (Union[Unset, str]):
            value (Union[Unset, Any]):
     """

    key: Union[Unset, str] = UNSET
    value: Union[Unset, Any] = UNSET





    def to_dict(self) -> dict[str, Any]:
        key = self.key

        value = self.value


        field_dict: dict[str, Any] = {}

        field_dict.update({
        })
        if key is not UNSET:
            field_dict["key"] = key
        if value is not UNSET:
            field_dict["value"] = value

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        key = d.pop("key", UNSET)

        value = d.pop("value", UNSET)

        record_tag_dto = cls(
            key=key,
            value=value,
        )

        return record_tag_dto

