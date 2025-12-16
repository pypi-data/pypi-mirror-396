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





T = TypeVar("T", bound="FailedUpsertItem")



@_attrs_define
class FailedUpsertItem:
    """ 
        Attributes:
            item (Union[Unset, UpsertRecordDto]):
            error (Union[Unset, str]):
     """

    item: Union[Unset, 'UpsertRecordDto'] = UNSET
    error: Union[Unset, str] = UNSET





    def to_dict(self) -> dict[str, Any]:
        from ..models.upsert_record_dto import UpsertRecordDto
        item: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.item, Unset):
            item = self.item.to_dict()

        error = self.error


        field_dict: dict[str, Any] = {}

        field_dict.update({
        })
        if item is not UNSET:
            field_dict["item"] = item
        if error is not UNSET:
            field_dict["error"] = error

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.upsert_record_dto import UpsertRecordDto
        d = dict(src_dict)
        _item = d.pop("item", UNSET)
        item: Union[Unset, UpsertRecordDto]
        if isinstance(_item,  Unset):
            item = UNSET
        else:
            item = UpsertRecordDto.from_dict(_item)




        error = d.pop("error", UNSET)

        failed_upsert_item = cls(
            item=item,
            error=error,
        )

        return failed_upsert_item

