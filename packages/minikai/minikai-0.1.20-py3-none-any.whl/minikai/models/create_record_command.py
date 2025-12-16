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
  from ..models.create_record_command_tags import CreateRecordCommandTags
  from ..models.record_authorization_dto import RecordAuthorizationDto





T = TypeVar("T", bound="CreateRecordCommand")



@_attrs_define
class CreateRecordCommand:
    """ 
        Attributes:
            title (Union[None, Unset, str]):
            description (Union[None, Unset, str]):
            mini_id (Union[None, Unset, str]):
            event_date (Union[None, Unset, datetime.datetime]):
            schema (Union[Unset, Any]):
            content (Union[Unset, Any]):
            relations (Union[Unset, list['RecordRelationDto']]):
            external_uri (Union[None, Unset, str]):
            labels (Union[Unset, list[str]]):
            tags (Union[Unset, CreateRecordCommandTags]):
            authorization (Union[Unset, RecordAuthorizationDto]):
            state (Union[Unset, RecordState]):
            batch_process (Union[Unset, bool]):
     """

    title: Union[None, Unset, str] = UNSET
    description: Union[None, Unset, str] = UNSET
    mini_id: Union[None, Unset, str] = UNSET
    event_date: Union[None, Unset, datetime.datetime] = UNSET
    schema: Union[Unset, Any] = UNSET
    content: Union[Unset, Any] = UNSET
    relations: Union[Unset, list['RecordRelationDto']] = UNSET
    external_uri: Union[None, Unset, str] = UNSET
    labels: Union[Unset, list[str]] = UNSET
    tags: Union[Unset, 'CreateRecordCommandTags'] = UNSET
    authorization: Union[Unset, 'RecordAuthorizationDto'] = UNSET
    state: Union[Unset, RecordState] = UNSET
    batch_process: Union[Unset, bool] = UNSET





    def to_dict(self) -> dict[str, Any]:
        from ..models.record_relation_dto import RecordRelationDto
        from ..models.create_record_command_tags import CreateRecordCommandTags
        from ..models.record_authorization_dto import RecordAuthorizationDto
        title: Union[None, Unset, str]
        if isinstance(self.title, Unset):
            title = UNSET
        else:
            title = self.title

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        mini_id: Union[None, Unset, str]
        if isinstance(self.mini_id, Unset):
            mini_id = UNSET
        else:
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



        external_uri: Union[None, Unset, str]
        if isinstance(self.external_uri, Unset):
            external_uri = UNSET
        else:
            external_uri = self.external_uri

        labels: Union[Unset, list[str]] = UNSET
        if not isinstance(self.labels, Unset):
            labels = self.labels



        tags: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.tags, Unset):
            tags = self.tags.to_dict()

        authorization: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.authorization, Unset):
            authorization = self.authorization.to_dict()

        state: Union[Unset, str] = UNSET
        if not isinstance(self.state, Unset):
            state = self.state


        batch_process = self.batch_process


        field_dict: dict[str, Any] = {}

        field_dict.update({
        })
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
        if external_uri is not UNSET:
            field_dict["externalUri"] = external_uri
        if labels is not UNSET:
            field_dict["labels"] = labels
        if tags is not UNSET:
            field_dict["tags"] = tags
        if authorization is not UNSET:
            field_dict["authorization"] = authorization
        if state is not UNSET:
            field_dict["state"] = state
        if batch_process is not UNSET:
            field_dict["batchProcess"] = batch_process

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.record_relation_dto import RecordRelationDto
        from ..models.create_record_command_tags import CreateRecordCommandTags
        from ..models.record_authorization_dto import RecordAuthorizationDto
        d = dict(src_dict)
        def _parse_title(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        title = _parse_title(d.pop("title", UNSET))


        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))


        def _parse_mini_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        mini_id = _parse_mini_id(d.pop("miniId", UNSET))


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


        def _parse_external_uri(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        external_uri = _parse_external_uri(d.pop("externalUri", UNSET))


        labels = cast(list[str], d.pop("labels", UNSET))


        _tags = d.pop("tags", UNSET)
        tags: Union[Unset, CreateRecordCommandTags]
        if isinstance(_tags,  Unset):
            tags = UNSET
        else:
            tags = CreateRecordCommandTags.from_dict(_tags)




        _authorization = d.pop("authorization", UNSET)
        authorization: Union[Unset, RecordAuthorizationDto]
        if isinstance(_authorization,  Unset):
            authorization = UNSET
        else:
            authorization = RecordAuthorizationDto.from_dict(_authorization)




        _state = d.pop("state", UNSET)
        state: Union[Unset, RecordState]
        if isinstance(_state,  Unset):
            state = UNSET
        else:
            state = check_record_state(_state)




        batch_process = d.pop("batchProcess", UNSET)

        create_record_command = cls(
            title=title,
            description=description,
            mini_id=mini_id,
            event_date=event_date,
            schema=schema,
            content=content,
            relations=relations,
            external_uri=external_uri,
            labels=labels,
            tags=tags,
            authorization=authorization,
            state=state,
            batch_process=batch_process,
        )

        return create_record_command

