from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.cursor_paginated_list_of_record_dto import CursorPaginatedListOfRecordDto
from ...models.record_state import check_record_state
from ...models.record_state import RecordState
from ...types import UNSET, Unset
from dateutil.parser import isoparse
from typing import cast
from typing import cast, Union
from typing import Union
import datetime



def _get_kwargs(
    *,
    mini_id: str,
    record_ids: Union[None, Unset, list[str]] = UNSET,
    session_id: Union[None, Unset, str] = UNSET,
    record_id: Union[None, Unset, str] = UNSET,
    before_cursor: Union[None, Unset, str] = UNSET,
    after_cursor: Union[None, Unset, str] = UNSET,
    limit_before: Union[None, Unset, int] = UNSET,
    limit_after: Union[None, Unset, int] = UNSET,
    labels: Union[None, Unset, list[str]] = UNSET,
    states: Union[None, Unset, list[RecordState]] = UNSET,
    start_date: Union[None, Unset, datetime.datetime] = UNSET,
    end_date: Union[None, Unset, datetime.datetime] = UNSET,
    created_by: Union[None, Unset, list[str]] = UNSET,
    updated_by: Union[None, Unset, list[str]] = UNSET,
    sort_descending: Union[Unset, bool] = True,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    params["miniId"] = mini_id

    json_record_ids: Union[None, Unset, list[str]]
    if isinstance(record_ids, Unset):
        json_record_ids = UNSET
    elif isinstance(record_ids, list):
        json_record_ids = record_ids


    else:
        json_record_ids = record_ids
    params["recordIds"] = json_record_ids

    json_session_id: Union[None, Unset, str]
    if isinstance(session_id, Unset):
        json_session_id = UNSET
    else:
        json_session_id = session_id
    params["sessionId"] = json_session_id

    json_record_id: Union[None, Unset, str]
    if isinstance(record_id, Unset):
        json_record_id = UNSET
    else:
        json_record_id = record_id
    params["recordId"] = json_record_id

    json_before_cursor: Union[None, Unset, str]
    if isinstance(before_cursor, Unset):
        json_before_cursor = UNSET
    else:
        json_before_cursor = before_cursor
    params["beforeCursor"] = json_before_cursor

    json_after_cursor: Union[None, Unset, str]
    if isinstance(after_cursor, Unset):
        json_after_cursor = UNSET
    else:
        json_after_cursor = after_cursor
    params["afterCursor"] = json_after_cursor

    json_limit_before: Union[None, Unset, int]
    if isinstance(limit_before, Unset):
        json_limit_before = UNSET
    else:
        json_limit_before = limit_before
    params["limitBefore"] = json_limit_before

    json_limit_after: Union[None, Unset, int]
    if isinstance(limit_after, Unset):
        json_limit_after = UNSET
    else:
        json_limit_after = limit_after
    params["limitAfter"] = json_limit_after

    json_labels: Union[None, Unset, list[str]]
    if isinstance(labels, Unset):
        json_labels = UNSET
    elif isinstance(labels, list):
        json_labels = labels


    else:
        json_labels = labels
    params["labels"] = json_labels

    json_states: Union[None, Unset, list[str]]
    if isinstance(states, Unset):
        json_states = UNSET
    elif isinstance(states, list):
        json_states = []
        for states_type_0_item_data in states:
            states_type_0_item: str = states_type_0_item_data
            json_states.append(states_type_0_item)


    else:
        json_states = states
    params["states"] = json_states

    json_start_date: Union[None, Unset, str]
    if isinstance(start_date, Unset):
        json_start_date = UNSET
    elif isinstance(start_date, datetime.datetime):
        json_start_date = start_date.isoformat()
    else:
        json_start_date = start_date
    params["startDate"] = json_start_date

    json_end_date: Union[None, Unset, str]
    if isinstance(end_date, Unset):
        json_end_date = UNSET
    elif isinstance(end_date, datetime.datetime):
        json_end_date = end_date.isoformat()
    else:
        json_end_date = end_date
    params["endDate"] = json_end_date

    json_created_by: Union[None, Unset, list[str]]
    if isinstance(created_by, Unset):
        json_created_by = UNSET
    elif isinstance(created_by, list):
        json_created_by = created_by


    else:
        json_created_by = created_by
    params["createdBy"] = json_created_by

    json_updated_by: Union[None, Unset, list[str]]
    if isinstance(updated_by, Unset):
        json_updated_by = UNSET
    elif isinstance(updated_by, list):
        json_updated_by = updated_by


    else:
        json_updated_by = updated_by
    params["updatedBy"] = json_updated_by

    params["sortDescending"] = sort_descending


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/Records",
        "params": params,
    }


    return _kwargs



def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[CursorPaginatedListOfRecordDto]:
    if response.status_code == 200:
        response_200 = CursorPaginatedListOfRecordDto.from_dict(response.json())



        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[CursorPaginatedListOfRecordDto]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    mini_id: str,
    record_ids: Union[None, Unset, list[str]] = UNSET,
    session_id: Union[None, Unset, str] = UNSET,
    record_id: Union[None, Unset, str] = UNSET,
    before_cursor: Union[None, Unset, str] = UNSET,
    after_cursor: Union[None, Unset, str] = UNSET,
    limit_before: Union[None, Unset, int] = UNSET,
    limit_after: Union[None, Unset, int] = UNSET,
    labels: Union[None, Unset, list[str]] = UNSET,
    states: Union[None, Unset, list[RecordState]] = UNSET,
    start_date: Union[None, Unset, datetime.datetime] = UNSET,
    end_date: Union[None, Unset, datetime.datetime] = UNSET,
    created_by: Union[None, Unset, list[str]] = UNSET,
    updated_by: Union[None, Unset, list[str]] = UNSET,
    sort_descending: Union[Unset, bool] = True,

) -> Response[CursorPaginatedListOfRecordDto]:
    """ 
    Args:
        mini_id (str):
        record_ids (Union[None, Unset, list[str]]):
        session_id (Union[None, Unset, str]):
        record_id (Union[None, Unset, str]):
        before_cursor (Union[None, Unset, str]):
        after_cursor (Union[None, Unset, str]):
        limit_before (Union[None, Unset, int]):
        limit_after (Union[None, Unset, int]):
        labels (Union[None, Unset, list[str]]):
        states (Union[None, Unset, list[RecordState]]):
        start_date (Union[None, Unset, datetime.datetime]):
        end_date (Union[None, Unset, datetime.datetime]):
        created_by (Union[None, Unset, list[str]]):
        updated_by (Union[None, Unset, list[str]]):
        sort_descending (Union[Unset, bool]):  Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CursorPaginatedListOfRecordDto]
     """


    kwargs = _get_kwargs(
        mini_id=mini_id,
record_ids=record_ids,
session_id=session_id,
record_id=record_id,
before_cursor=before_cursor,
after_cursor=after_cursor,
limit_before=limit_before,
limit_after=limit_after,
labels=labels,
states=states,
start_date=start_date,
end_date=end_date,
created_by=created_by,
updated_by=updated_by,
sort_descending=sort_descending,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    mini_id: str,
    record_ids: Union[None, Unset, list[str]] = UNSET,
    session_id: Union[None, Unset, str] = UNSET,
    record_id: Union[None, Unset, str] = UNSET,
    before_cursor: Union[None, Unset, str] = UNSET,
    after_cursor: Union[None, Unset, str] = UNSET,
    limit_before: Union[None, Unset, int] = UNSET,
    limit_after: Union[None, Unset, int] = UNSET,
    labels: Union[None, Unset, list[str]] = UNSET,
    states: Union[None, Unset, list[RecordState]] = UNSET,
    start_date: Union[None, Unset, datetime.datetime] = UNSET,
    end_date: Union[None, Unset, datetime.datetime] = UNSET,
    created_by: Union[None, Unset, list[str]] = UNSET,
    updated_by: Union[None, Unset, list[str]] = UNSET,
    sort_descending: Union[Unset, bool] = True,

) -> Optional[CursorPaginatedListOfRecordDto]:
    """ 
    Args:
        mini_id (str):
        record_ids (Union[None, Unset, list[str]]):
        session_id (Union[None, Unset, str]):
        record_id (Union[None, Unset, str]):
        before_cursor (Union[None, Unset, str]):
        after_cursor (Union[None, Unset, str]):
        limit_before (Union[None, Unset, int]):
        limit_after (Union[None, Unset, int]):
        labels (Union[None, Unset, list[str]]):
        states (Union[None, Unset, list[RecordState]]):
        start_date (Union[None, Unset, datetime.datetime]):
        end_date (Union[None, Unset, datetime.datetime]):
        created_by (Union[None, Unset, list[str]]):
        updated_by (Union[None, Unset, list[str]]):
        sort_descending (Union[Unset, bool]):  Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CursorPaginatedListOfRecordDto
     """


    return sync_detailed(
        client=client,
mini_id=mini_id,
record_ids=record_ids,
session_id=session_id,
record_id=record_id,
before_cursor=before_cursor,
after_cursor=after_cursor,
limit_before=limit_before,
limit_after=limit_after,
labels=labels,
states=states,
start_date=start_date,
end_date=end_date,
created_by=created_by,
updated_by=updated_by,
sort_descending=sort_descending,

    ).parsed

async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    mini_id: str,
    record_ids: Union[None, Unset, list[str]] = UNSET,
    session_id: Union[None, Unset, str] = UNSET,
    record_id: Union[None, Unset, str] = UNSET,
    before_cursor: Union[None, Unset, str] = UNSET,
    after_cursor: Union[None, Unset, str] = UNSET,
    limit_before: Union[None, Unset, int] = UNSET,
    limit_after: Union[None, Unset, int] = UNSET,
    labels: Union[None, Unset, list[str]] = UNSET,
    states: Union[None, Unset, list[RecordState]] = UNSET,
    start_date: Union[None, Unset, datetime.datetime] = UNSET,
    end_date: Union[None, Unset, datetime.datetime] = UNSET,
    created_by: Union[None, Unset, list[str]] = UNSET,
    updated_by: Union[None, Unset, list[str]] = UNSET,
    sort_descending: Union[Unset, bool] = True,

) -> Response[CursorPaginatedListOfRecordDto]:
    """ 
    Args:
        mini_id (str):
        record_ids (Union[None, Unset, list[str]]):
        session_id (Union[None, Unset, str]):
        record_id (Union[None, Unset, str]):
        before_cursor (Union[None, Unset, str]):
        after_cursor (Union[None, Unset, str]):
        limit_before (Union[None, Unset, int]):
        limit_after (Union[None, Unset, int]):
        labels (Union[None, Unset, list[str]]):
        states (Union[None, Unset, list[RecordState]]):
        start_date (Union[None, Unset, datetime.datetime]):
        end_date (Union[None, Unset, datetime.datetime]):
        created_by (Union[None, Unset, list[str]]):
        updated_by (Union[None, Unset, list[str]]):
        sort_descending (Union[Unset, bool]):  Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CursorPaginatedListOfRecordDto]
     """


    kwargs = _get_kwargs(
        mini_id=mini_id,
record_ids=record_ids,
session_id=session_id,
record_id=record_id,
before_cursor=before_cursor,
after_cursor=after_cursor,
limit_before=limit_before,
limit_after=limit_after,
labels=labels,
states=states,
start_date=start_date,
end_date=end_date,
created_by=created_by,
updated_by=updated_by,
sort_descending=sort_descending,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    mini_id: str,
    record_ids: Union[None, Unset, list[str]] = UNSET,
    session_id: Union[None, Unset, str] = UNSET,
    record_id: Union[None, Unset, str] = UNSET,
    before_cursor: Union[None, Unset, str] = UNSET,
    after_cursor: Union[None, Unset, str] = UNSET,
    limit_before: Union[None, Unset, int] = UNSET,
    limit_after: Union[None, Unset, int] = UNSET,
    labels: Union[None, Unset, list[str]] = UNSET,
    states: Union[None, Unset, list[RecordState]] = UNSET,
    start_date: Union[None, Unset, datetime.datetime] = UNSET,
    end_date: Union[None, Unset, datetime.datetime] = UNSET,
    created_by: Union[None, Unset, list[str]] = UNSET,
    updated_by: Union[None, Unset, list[str]] = UNSET,
    sort_descending: Union[Unset, bool] = True,

) -> Optional[CursorPaginatedListOfRecordDto]:
    """ 
    Args:
        mini_id (str):
        record_ids (Union[None, Unset, list[str]]):
        session_id (Union[None, Unset, str]):
        record_id (Union[None, Unset, str]):
        before_cursor (Union[None, Unset, str]):
        after_cursor (Union[None, Unset, str]):
        limit_before (Union[None, Unset, int]):
        limit_after (Union[None, Unset, int]):
        labels (Union[None, Unset, list[str]]):
        states (Union[None, Unset, list[RecordState]]):
        start_date (Union[None, Unset, datetime.datetime]):
        end_date (Union[None, Unset, datetime.datetime]):
        created_by (Union[None, Unset, list[str]]):
        updated_by (Union[None, Unset, list[str]]):
        sort_descending (Union[Unset, bool]):  Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CursorPaginatedListOfRecordDto
     """


    return (await asyncio_detailed(
        client=client,
mini_id=mini_id,
record_ids=record_ids,
session_id=session_id,
record_id=record_id,
before_cursor=before_cursor,
after_cursor=after_cursor,
limit_before=limit_before,
limit_after=limit_after,
labels=labels,
states=states,
start_date=start_date,
end_date=end_date,
created_by=created_by,
updated_by=updated_by,
sort_descending=sort_descending,

    )).parsed
