from dataclasses import dataclass, field
from typing import List
from pymementodb.field import Field
from pymementodb.helpers import transform_str_to_dt


@dataclass(frozen=True)
class Library:
    id: str
    name: str = field(compare=False)
    owner: str = field(repr=False, compare=False)
    createdTime: str = field(repr=False, compare=False)
    modifiedTime: str = field(repr=False, compare=False)
    size: int = field(repr=False, compare=False)
    revision: int = field(repr=False, compare=False)
    fields: List[Field] = field(repr=False, compare=False)

    def __post_init__(self):
        object.__setattr__(self, 'createdTime', transform_str_to_dt(self.createdTime))
        object.__setattr__(self, 'modifiedTime', transform_str_to_dt(self.modifiedTime))
        for i, field_data in enumerate(self.fields):
            self.fields[i] = Field(lib_id = self.id, **field_data)
