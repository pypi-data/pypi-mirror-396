from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.upsert_record_dto import UpsertRecordDto





T = TypeVar("T", bound="UpsertRecordsByExternalUriCommand")



@_attrs_define
class UpsertRecordsByExternalUriCommand:
    """ 
        Attributes:
            items (Union[Unset, list['UpsertRecordDto']]):
     """

    items: Union[Unset, list['UpsertRecordDto']] = UNSET





    def to_dict(self) -> dict[str, Any]:
        from ..models.upsert_record_dto import UpsertRecordDto
        items: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.items, Unset):
            items = []
            for items_item_data in self.items:
                items_item = items_item_data.to_dict()
                items.append(items_item)




        field_dict: dict[str, Any] = {}

        field_dict.update({
        })
        if items is not UNSET:
            field_dict["items"] = items

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.upsert_record_dto import UpsertRecordDto
        d = dict(src_dict)
        items = []
        _items = d.pop("items", UNSET)
        for items_item_data in (_items or []):
            items_item = UpsertRecordDto.from_dict(items_item_data)



            items.append(items_item)


        upsert_records_by_external_uri_command = cls(
            items=items,
        )

        return upsert_records_by_external_uri_command

