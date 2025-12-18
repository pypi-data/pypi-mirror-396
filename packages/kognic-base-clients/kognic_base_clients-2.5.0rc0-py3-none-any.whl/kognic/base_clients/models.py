from typing import Dict, Optional, Union

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class BaseSerializer(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel, from_attributes=True)

    @classmethod
    def from_json(cls, js: Dict):
        return cls.model_validate(js)

    def to_dict(self, by_alias=True) -> Dict:
        return self.model_dump(exclude_none=True, by_alias=by_alias)


CursorIdType = Union[int, str]


class PageMetadata(BaseSerializer):
    next_cursor_id: Optional[CursorIdType] = None


class PaginatedResponse(BaseSerializer):
    data: Union[dict, list]
    metadata: PageMetadata = PageMetadata()
