from dataclasses_json import dataclass_json
from pydantic.dataclasses import dataclass
from datetime import datetime


@dataclass_json
@dataclass
class Deck:
    deck_id: int = 0
    deck_uuid: str = ""
    deck_name: str = ""
    user_user_id: int = 0
    is_in_set: bool = False
    is_public: bool = False
    created: datetime = datetime.utcnow()
    modified: datetime = datetime.utcnow()
    is_deleted: bool = False
