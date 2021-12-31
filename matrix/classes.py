from typing import List, Mapping
from dataclasses import dataclass


@dataclass
class Authentication:
    """Class to keep authentication data."""
    access_token: str
    home_server: str
    user_id: str
    device_id: str


@dataclass
class Message:
    """Class to keep message data."""
    type: str
    body: str
    format: str = None
    formatted_body: str = None


@dataclass
class Event:
    """Class to keep event data."""
    event_id: str = None
    type: str = None
    content: dict = None
    timestamp: int = None
    sender: str = None
    parsed_message: Message = None
    state_key: str = None


@dataclass
class Room:
    """Class to keep room data."""
    timeline: List[Event]
    state: dict
    account_data: dict
    unread_notifications: dict
    summary: dict
    unread_count: int
    id: str
    encrypted: bool


@dataclass
class Invite_State:
    """Class to keep invite state data."""
    events: List[Event]


@dataclass
class Invite:
    """Class to keep invite data"""
    invite_state: Invite_State
    room_id: str
    invitee: str


@dataclass
class State:
    """Class to keep state data."""
    next_batch: str = None
    account_data: dict = None
    joined_rooms: List[Room] = None
    invited_rooms: List[Invite] = None


@dataclass
class Timeline:
    """Class to keep timeline data."""
    events: List[Event]
    prev_batch: str
    limited: bool


@dataclass
class Unread_Notification:
    """Class to keep unread notification data."""
    notification_count: int
    highlight_count: int


@dataclass
class User:
    """Class to keep user data."""
    user_id: str
    device_id: str = None
    is_guest: bool = None
    displayname: str = None
    avatar_url: str = None


class Room_Preset:
    """Class to keep room preset data."""
    private_chat: str = "private_chat"
    trusted_private_chat: str = "trusted_private_chat"
    public_chat: str = "public_chat"


@dataclass
class Device_Keys:
    """Class to keep device keys data."""
    algorithms: List[str]
    device_id: str
    keys: Mapping[str, str]
    user_id: str
    unsigned: Mapping[str, str]
    signatures: Mapping[str, Mapping[str, str]]


@dataclass
class Device_Keys_Response:
    """Class to keep device keys response data."""
    device_keys: Mapping[str, List[Device_Keys]]
    failures: dict
    master_keys: dict
    self_signing_keys: dict
    user_signing_keys: dict
