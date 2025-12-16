from typing import Literal, cast

RecordState = Literal['active', 'archived', 'deleted', 'draft', 'processing']

RECORD_STATE_VALUES: set[RecordState] = { 'active', 'archived', 'deleted', 'draft', 'processing',  }

def check_record_state(value: str) -> RecordState:
    if value in RECORD_STATE_VALUES:
        return cast(RecordState, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {RECORD_STATE_VALUES!r}")
