from dataclasses_json import dataclass_json
from pydantic.dataclasses import dataclass
from dataclasses import field
from datetime import datetime

from models.token import Token


@dataclass_json
@dataclass
class User:
    token: Token = field(default_factory=Token)
    xp_count: int = 0

    user_id: int = 0
    user_uuid: str = ""
    user_name: str = ""
    user_email: str = ""
    session_token: str = ""
    hashed_password: str = ""
    password_salt: str = ""
    email_verified: bool = False
    random_id: int = 0
    modified: datetime = datetime.now()
    created: datetime = datetime.now()
    is_deleted: bool = False
