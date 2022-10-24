from dataclasses_json import dataclass_json
from pydantic.dataclasses import dataclass
from datetime import datetime


@dataclass_json
@dataclass
class FriendRequest:
    friend_request_id: int = 0
    friend_request_uuid: str = ""
    sender_user_id: int = 0
    receiver_user_id: int = 0
    is_accepted: bool = False
    modified: datetime = datetime.now()
    created: datetime = datetime.now()
    is_deleted: bool = False
