from dataclasses_json import dataclass_json
from pydantic.dataclasses import dataclass
from dataclasses import field
from datetime import datetime

from models.token import Token


@dataclass_json
@dataclass
class User:
    token: Token = field(default_factory=Token)

    user_id: int = 0
    user_uuid: str = ""
    user_name: str = ""
    session_token: str = ""
    password_hash: str = ""
    password_salt: str = ""
    modified: datetime = datetime.utcnow()
    created: datetime = datetime.utcnow()
    is_deleted: bool = False
