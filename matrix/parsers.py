from .classes import *
from typing import List


def parse_event(event: dict) -> Event:
    """Parse event data."""
    return Event(
        event_id=event.get("event_id"),
        type=event.get("type"),
        content=event.get("content"),
        timestamp=event.get("origin_server_ts"),
        sender=event.get("sender"),
        state_key=event.get("state_key"),
        parsed_message=parse_message(event["content"]) if event.get("content")
        and event["type"] == "m.room.message" else None)


def parse_notification(notification: dict) -> Unread_Notification:
    """Parse unread notification data."""
    return Unread_Notification(
        notification_count=notification["notification_count"],
        highlight_count=notification["highlight_count"])


def check_if_encrypted(room: Room) -> bool:
    """Check if room is encrypted."""
    for event in room.timeline:
        if event.type == "m.room.encryption" and event.content.get(
                "algorithm") == "m.megolm.v1.aes-sha2":
            return True
    return False


def parse_room(room: dict, room_id: str) -> Room:
    """Parse room data."""
    r = Room(
        timeline=[parse_event(event) for event in room["timeline"]["events"]],
        state=room["state"],
        account_data=room["account_data"],
        unread_notifications=parse_notification(room["unread_notifications"]),
        summary=room["summary"],
        unread_count=room["org.matrix.msc2654.unread_count"],
        id=room_id,
        encrypted=None)

    r.encrypted = check_if_encrypted(r)
    return r


def parse_account_data(data: dict) -> List[Event]:
    """Parse account data."""
    events = []
    for event in data["events"]:
        events.append(parse_event(event))
    return events


def parse_state(state: dict) -> State:
    """Parse state data."""
    return State(
        next_batch=state.get("content"),
        account_data=state.get("account_data"),
        joined_rooms=[
            parse_room(state["rooms"]["join"][room], room)
            for room in state["rooms"]["join"]
        ] if state.get("rooms", {}).get("join") else [],
        invited_rooms=[
            parse_invite(state["rooms"]["invite"][room], room)
            for room in state["rooms"]["invite"]
        ] if state.get("rooms", {}).get("invite") else [],
    )


def parse_message(message: dict) -> Message:
    """Parse message data."""
    return Message(type=message.get("msgtype"),
                   body=message.get("body"),
                   format=message.get("format"),
                   formatted_body=message.get("formatted_body"))


def parse_room_events(events: dict) -> List[Event]:
    """Parse room events data."""
    events = [parse_event(event) for event in events]
    for e in events:
        if e.type == "m.room.message":
            e.parsed_message = parse_message(e.content)
    return events


def get_invitee_from_events(events: List[Event]) -> str:
    """Get invitee from events."""
    for event in events:
        if event.type == "m.room.member" and event.content.get(
                "membership") == "invite":
            return event.sender
    return None


def parse_invite(invite: dict, room_id: str) -> Invite:
    """Parse invite data."""
    events = [parse_event(event) for event in invite["invite_state"]["events"]]
    return Invite(
        invite_state=Invite_State(events=events, ),
        room_id=room_id,
        invitee=get_invitee_from_events(events),
    )


def parse_device_key(data: dict) -> Device_Keys:
    """Parse device key data."""
    return Device_Keys(
        algorithms=data.get("algorithms"),
        device_id=data.get("device_id"),
        keys=data.get("keys"),
        user_id=data.get("user_id"),
        unsigned=data.get("unsigned"),
        signatures=data.get("signatures"),
    )


def parse_device_keys_response(data: dict) -> Device_Keys_Response:
    """Parse device keys data."""

    keys = {}  # Mapping[str, List[Device_Keys]]
    for user in data["device_keys"]:
        for key in data["device_keys"][user]:
            keys[user].append(parse_device_key(key))

    return Device_Keys_Response(
        user_signing_keys=data.get("user_signing_keys"),
        self_signing_keys=data.get("self_signing_keys"),
        master_keys=data.get("master_keys"),
        failures=data.get("failures"),
        device_keys=keys)
