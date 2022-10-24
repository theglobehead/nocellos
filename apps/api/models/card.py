from dataclasses_json import dataclass_json
from pydantic.dataclasses import dataclass
from datetime import datetime


@dataclass_json
@dataclass
class Card:
    card_id: int = 0
    card_uuid: str = ""
    front_text: str = ""
    back_text: str = ""
    deck_deck_id: int = 0
    created: datetime = datetime.utcnow()
    modified: datetime = datetime.utcnow()
    is_deleted: bool = False
