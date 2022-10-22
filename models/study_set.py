from dataclasses_json import dataclass_json
from pydantic.dataclasses import dataclass
from datetime import datetime


@dataclass_json
@dataclass
class StudySet:
    study_set_id: int = 0
    study_set_uuid: str = ""
    study_set_name: str = ""
    creator_user_id: int = 0
    is_public: bool = False
    created: datetime = datetime.utcnow()
    modified: datetime = datetime.utcnow()
    is_deleted: bool = False
