from typing import Literal, cast

WorkspaceType = Literal['ndis', 'rac', 'sah']

WORKSPACE_TYPE_VALUES: set[WorkspaceType] = { 'ndis', 'rac', 'sah',  }

def check_workspace_type(value: str) -> WorkspaceType:
    if value in WORKSPACE_TYPE_VALUES:
        return cast(WorkspaceType, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {WORKSPACE_TYPE_VALUES!r}")
