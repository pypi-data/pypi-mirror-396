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
  from ..models.record_dto import RecordDto





T = TypeVar("T", bound="CursorPaginatedListOfRecordDto")



@_attrs_define
class CursorPaginatedListOfRecordDto:
    """ 
        Attributes:
            items (Union[Unset, list['RecordDto']]):
            before_cursor (Union[None, Unset, str]):
            after_cursor (Union[None, Unset, str]):
     """

    items: Union[Unset, list['RecordDto']] = UNSET
    before_cursor: Union[None, Unset, str] = UNSET
    after_cursor: Union[None, Unset, str] = UNSET





    def to_dict(self) -> dict[str, Any]:
        from ..models.record_dto import RecordDto
        items: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.items, Unset):
            items = []
            for items_item_data in self.items:
                items_item = items_item_data.to_dict()
                items.append(items_item)



        before_cursor: Union[None, Unset, str]
        if isinstance(self.before_cursor, Unset):
            before_cursor = UNSET
        else:
            before_cursor = self.before_cursor

        after_cursor: Union[None, Unset, str]
        if isinstance(self.after_cursor, Unset):
            after_cursor = UNSET
        else:
            after_cursor = self.after_cursor


        field_dict: dict[str, Any] = {}

        field_dict.update({
        })
        if items is not UNSET:
            field_dict["items"] = items
        if before_cursor is not UNSET:
            field_dict["beforeCursor"] = before_cursor
        if after_cursor is not UNSET:
            field_dict["afterCursor"] = after_cursor

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.record_dto import RecordDto
        d = dict(src_dict)
        items = []
        _items = d.pop("items", UNSET)
        for items_item_data in (_items or []):
            items_item = RecordDto.from_dict(items_item_data)



            items.append(items_item)


        def _parse_before_cursor(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        before_cursor = _parse_before_cursor(d.pop("beforeCursor", UNSET))


        def _parse_after_cursor(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        after_cursor = _parse_after_cursor(d.pop("afterCursor", UNSET))


        cursor_paginated_list_of_record_dto = cls(
            items=items,
            before_cursor=before_cursor,
            after_cursor=after_cursor,
        )

        return cursor_paginated_list_of_record_dto

