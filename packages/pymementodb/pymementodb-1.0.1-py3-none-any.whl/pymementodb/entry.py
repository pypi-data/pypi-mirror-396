from dataclasses import dataclass, field
from pymementodb.helpers import transform_str_to_dt


@dataclass(frozen=True)
class Entry:
    id: str
    lib_id: str
    author: str = field(compare=False)
    createdTime: str = field(repr=False, compare=False)
    modifiedTime: str = field(repr=False, compare=False)
    revision: int = field(repr=False, compare=False)
    status: str = field(repr=False, compare=False)
    size: int = field(repr=False, compare=False)
    fields: list = field(repr=False, compare=False)

    def __post_init__(self):
        object.__setattr__(self, 'createdTime', transform_str_to_dt(self.createdTime))
        object.__setattr__(self, 'modifiedTime', transform_str_to_dt(self.modifiedTime))
        # transform datetime strings (where available) in field values
        for i, field in enumerate(self.fields):
            try:
                self.fields[i]['value'] = transform_str_to_dt(field['value'])
            except (ValueError, AttributeError):
                continue

    def get_field_value(self, id: int):
        """Return the value of the field.

        Args:
            id: id of the field for which the value should be returned.

        Returns:
            value of the field or None if field with id is not present
        """
        for field in self.fields:
            if field['id'] == id:
                return field['value']
        else:
            return None
