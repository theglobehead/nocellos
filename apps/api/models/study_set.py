from dataclasses import field
from typing import List

from dataclasses_json import dataclass_json
from pydantic.dataclasses import dataclass
from datetime import datetime

from models.label import Label


@dataclass_json
@dataclass
class StudySet:
    deck_count: int = 0
    can_edit: bool = False
    labels: List[Label] = field(default_factory=list)

    study_set_id: int = 0
    study_set_uuid: str = ""
    study_set_name: str = ""
    creator_user_id: int = 0
    is_public: bool = False
    created: datetime = datetime.utcnow()
    modified: datetime = datetime.utcnow()
    is_deleted: bool = False
