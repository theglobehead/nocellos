from dataclasses import field
from typing import List

from dataclasses_json import dataclass_json
from pydantic.dataclasses import dataclass
from datetime import datetime

from models.card import Card


@dataclass_json
@dataclass
class Deck:
    card_count: int = 0
    labels: List[Card] = field(default_factory=List)

    deck_id: int = 0
    deck_uuid: str = ""
    deck_name: str = ""
    user_user_id: int = 0
    is_in_set: bool = False
    is_public: bool = False
    created: datetime = datetime.utcnow()
    modified: datetime = datetime.utcnow()
    is_deleted: bool = False
