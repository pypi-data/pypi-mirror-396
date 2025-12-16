from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Union

if TYPE_CHECKING:
  from ..models.batch_upsert_result_successful_ids import BatchUpsertResultSuccessfulIds
  from ..models.failed_upsert_item import FailedUpsertItem





T = TypeVar("T", bound="BatchUpsertResult")



@_attrs_define
class BatchUpsertResult:
    """ 
        Attributes:
            successful_ids (Union[Unset, BatchUpsertResultSuccessfulIds]):
            failed (Union[Unset, list['FailedUpsertItem']]):
            success_count (Union[Unset, int]):
            failure_count (Union[Unset, int]):
     """

    successful_ids: Union[Unset, 'BatchUpsertResultSuccessfulIds'] = UNSET
    failed: Union[Unset, list['FailedUpsertItem']] = UNSET
    success_count: Union[Unset, int] = UNSET
    failure_count: Union[Unset, int] = UNSET





    def to_dict(self) -> dict[str, Any]:
        from ..models.batch_upsert_result_successful_ids import BatchUpsertResultSuccessfulIds
        from ..models.failed_upsert_item import FailedUpsertItem
        successful_ids: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.successful_ids, Unset):
            successful_ids = self.successful_ids.to_dict()

        failed: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.failed, Unset):
            failed = []
            for failed_item_data in self.failed:
                failed_item = failed_item_data.to_dict()
                failed.append(failed_item)



        success_count = self.success_count

        failure_count = self.failure_count


        field_dict: dict[str, Any] = {}

        field_dict.update({
        })
        if successful_ids is not UNSET:
            field_dict["successfulIds"] = successful_ids
        if failed is not UNSET:
            field_dict["failed"] = failed
        if success_count is not UNSET:
            field_dict["successCount"] = success_count
        if failure_count is not UNSET:
            field_dict["failureCount"] = failure_count

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.batch_upsert_result_successful_ids import BatchUpsertResultSuccessfulIds
        from ..models.failed_upsert_item import FailedUpsertItem
        d = dict(src_dict)
        _successful_ids = d.pop("successfulIds", UNSET)
        successful_ids: Union[Unset, BatchUpsertResultSuccessfulIds]
        if isinstance(_successful_ids,  Unset):
            successful_ids = UNSET
        else:
            successful_ids = BatchUpsertResultSuccessfulIds.from_dict(_successful_ids)




        failed = []
        _failed = d.pop("failed", UNSET)
        for failed_item_data in (_failed or []):
            failed_item = FailedUpsertItem.from_dict(failed_item_data)



            failed.append(failed_item)


        success_count = d.pop("successCount", UNSET)

        failure_count = d.pop("failureCount", UNSET)

        batch_upsert_result = cls(
            successful_ids=successful_ids,
            failed=failed,
            success_count=success_count,
            failure_count=failure_count,
        )

        return batch_upsert_result

