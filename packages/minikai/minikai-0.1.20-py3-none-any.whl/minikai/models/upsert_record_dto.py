from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.record_state import check_record_state
from ..models.record_state import RecordState
from ..types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from typing import cast, Union
from typing import Union
import datetime

if TYPE_CHECKING:
  from ..models.record_relation_dto import RecordRelationDto
  from ..models.upsert_record_dto_tags import UpsertRecordDtoTags
  from ..models.record_authorization_dto import RecordAuthorizationDto





T = TypeVar("T", bound="UpsertRecordDto")



@_attrs_define
class UpsertRecordDto:
    """ 
        Attributes:
            external_uri (Union[Unset, str]):
            title (Union[Unset, str]):
            description (Union[None, Unset, str]):
            mini_id (Union[Unset, str]):
            event_date (Union[None, Unset, datetime.datetime]):
            schema (Union[Unset, Any]):
            content (Union[Unset, Any]):
            relations (Union[Unset, list['RecordRelationDto']]):
            labels (Union[Unset, list[str]]):
            tags (Union[Unset, UpsertRecordDtoTags]):
            authorization (Union['RecordAuthorizationDto', None, Unset]):
            state (Union[None, RecordState, Unset]):
     """

    external_uri: Union[Unset, str] = UNSET
    title: Union[Unset, str] = UNSET
    description: Union[None, Unset, str] = UNSET
    mini_id: Union[Unset, str] = UNSET
    event_date: Union[None, Unset, datetime.datetime] = UNSET
    schema: Union[Unset, Any] = UNSET
    content: Union[Unset, Any] = UNSET
    relations: Union[Unset, list['RecordRelationDto']] = UNSET
    labels: Union[Unset, list[str]] = UNSET
    tags: Union[Unset, 'UpsertRecordDtoTags'] = UNSET
    authorization: Union['RecordAuthorizationDto', None, Unset] = UNSET
    state: Union[None, RecordState, Unset] = UNSET





    def to_dict(self) -> dict[str, Any]:
        from ..models.record_relation_dto import RecordRelationDto
        from ..models.upsert_record_dto_tags import UpsertRecordDtoTags
        from ..models.record_authorization_dto import RecordAuthorizationDto
        external_uri = self.external_uri

        title = self.title

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        mini_id = self.mini_id

        event_date: Union[None, Unset, str]
        if isinstance(self.event_date, Unset):
            event_date = UNSET
        elif isinstance(self.event_date, datetime.datetime):
            event_date = self.event_date.isoformat()
        else:
            event_date = self.event_date

        schema = self.schema

        content = self.content

        relations: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.relations, Unset):
            relations = []
            for relations_item_data in self.relations:
                relations_item = relations_item_data.to_dict()
                relations.append(relations_item)



        labels: Union[Unset, list[str]] = UNSET
        if not isinstance(self.labels, Unset):
            labels = self.labels



        tags: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.tags, Unset):
            tags = self.tags.to_dict()

        authorization: Union[None, Unset, dict[str, Any]]
        if isinstance(self.authorization, Unset):
            authorization = UNSET
        elif isinstance(self.authorization, RecordAuthorizationDto):
            authorization = self.authorization.to_dict()
        else:
            authorization = self.authorization

        state: Union[None, Unset, str]
        if isinstance(self.state, Unset):
            state = UNSET
        elif isinstance(self.state, str):
            state = self.state
        else:
            state = self.state


        field_dict: dict[str, Any] = {}

        field_dict.update({
        })
        if external_uri is not UNSET:
            field_dict["externalUri"] = external_uri
        if title is not UNSET:
            field_dict["title"] = title
        if description is not UNSET:
            field_dict["description"] = description
        if mini_id is not UNSET:
            field_dict["miniId"] = mini_id
        if event_date is not UNSET:
            field_dict["eventDate"] = event_date
        if schema is not UNSET:
            field_dict["schema"] = schema
        if content is not UNSET:
            field_dict["content"] = content
        if relations is not UNSET:
            field_dict["relations"] = relations
        if labels is not UNSET:
            field_dict["labels"] = labels
        if tags is not UNSET:
            field_dict["tags"] = tags
        if authorization is not UNSET:
            field_dict["authorization"] = authorization
        if state is not UNSET:
            field_dict["state"] = state

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.record_relation_dto import RecordRelationDto
        from ..models.upsert_record_dto_tags import UpsertRecordDtoTags
        from ..models.record_authorization_dto import RecordAuthorizationDto
        d = dict(src_dict)
        external_uri = d.pop("externalUri", UNSET)

        title = d.pop("title", UNSET)

        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))


        mini_id = d.pop("miniId", UNSET)

        def _parse_event_date(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                event_date_type_0 = isoparse(data)



                return event_date_type_0
            except: # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        event_date = _parse_event_date(d.pop("eventDate", UNSET))


        schema = d.pop("schema", UNSET)

        content = d.pop("content", UNSET)

        relations = []
        _relations = d.pop("relations", UNSET)
        for relations_item_data in (_relations or []):
            relations_item = RecordRelationDto.from_dict(relations_item_data)



            relations.append(relations_item)


        labels = cast(list[str], d.pop("labels", UNSET))


        _tags = d.pop("tags", UNSET)
        tags: Union[Unset, UpsertRecordDtoTags]
        if isinstance(_tags,  Unset):
            tags = UNSET
        else:
            tags = UpsertRecordDtoTags.from_dict(_tags)




        def _parse_authorization(data: object) -> Union['RecordAuthorizationDto', None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                authorization_type_0 = RecordAuthorizationDto.from_dict(data)



                return authorization_type_0
            except: # noqa: E722
                pass
            return cast(Union['RecordAuthorizationDto', None, Unset], data)

        authorization = _parse_authorization(d.pop("authorization", UNSET))


        def _parse_state(data: object) -> Union[None, RecordState, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                state_type_0 = check_record_state(data)



                return state_type_0
            except: # noqa: E722
                pass
            return cast(Union[None, RecordState, Unset], data)

        state = _parse_state(d.pop("state", UNSET))


        upsert_record_dto = cls(
            external_uri=external_uri,
            title=title,
            description=description,
            mini_id=mini_id,
            event_date=event_date,
            schema=schema,
            content=content,
            relations=relations,
            labels=labels,
            tags=tags,
            authorization=authorization,
            state=state,
        )

        return upsert_record_dto

