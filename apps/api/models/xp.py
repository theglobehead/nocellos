from dataclasses_json import dataclass_json
from pydantic.dataclasses import dataclass
from datetime import datetime


@dataclass_json
@dataclass
class Xp:
    xp_id: int = 0
    xp_count: int = 0
    user_user_id: int = 0
    created: datetime = datetime.utcnow()
    modified: datetime = datetime.utcnow()
    is_deleted: bool = False
