from .classes import Authentication, Device_Keys_Response, Event, Room_Preset, State, User
from .parsers import parse_event, parse_room_events, parse_state, parse_device_keys_response
from .e2ee import Olm
from .exceptions import *
from typing import Any, Dict, List, Mapping
import threading
import requests
from time import time, sleep
from .constants import Constants

try:
    from urllib import quote
except ImportError:
    from urllib.parse import quote

MATRIX_V2_API_PATH = Constants.V2_API_PATH

# https://github.com/matrix-org/matrix-python-sdk/blob/master/matrix_client/api.py
# https://matrix.org/docs/guides/client-server-api
# https://spec.matrix.org/v1.1/client-server-api/
# https://matrix.org/docs/spec/client_server/r0.4.0#post-matrix-client-r0-keys-upload
# https://github.com/matrix-org/matrix-doc/blob/main/proposals/1772-groups-as-rooms.md


class Bot():
    def __init__(self,
                 homeserver: str,
                 username: str,
                 password: str,
                 sync_delay: int = 2,
                 device_id: str = "") -> None:
        """
        Initialize the client.

        :param homeserver: The homeserver url.
        :param username: The username.
        :param password: The password.
        :param sync_delay: The sync delay.

        """
        self.base = homeserver
        self.user = username
        self.pwd = password
        self.device_id = device_id
        self.auth = None
        self.use_auth_header = True
        self.state = State(next_batch="")
        self.set_as_online = True
        self.sync_delay = sync_delay
        self.run = True
        self.txn_id = 0

        # self.mongo_db = MongoDB
        self.olm = Olm()

    def stop(self) -> None:
        """Stop the sync thread."""
        self.run = False

    def _make_request(self,
                      method: str,
                      endpoint: str,
                      data: dict = {},
                      params: dict = {},
                      skip_auth_check: bool = False,
                      API_path: str = "/_matrix/client/r0",
                      raw_data: Any = None,
                      headers: Dict[str, str] = {}) -> dict:
        """
        Make a request to the homeserver.

        :param method: HTTP method
        :param endpoint: Endpoint
        :param data: JSON data to send
        :param params: Parameters
        :param skip_auth_check: Skip the auth check
        :param API_path: API path
        :param raw_data: Raw data
        :param headers: HTTP Headers
        :return: Response from the homeserver
        """

        method = method.upper()
        if method not in ["GET", "PUT", "DELETE", "POST"]:
            print(f"[!] Invalid method: {method}")
            return None

        headers = {"Content-Type": "application/json"}

        if not self.auth and not skip_auth_check:
            # print("[!] Not authenticated")
            raise NotAuthenticated("Not authenticated")
            # return None

        elif self.auth:
            if self.use_auth_header:
                headers["Authorization"] = f"Bearer {self.auth.access_token}"
            else:
                params["access_token"] = self.auth.access_token

        r = requests.request(method,
                             f"{self.base}{API_path}{endpoint}",
                             params=params,
                             json=data,
                             data=raw_data,
                             headers=headers)

        try:
            if not r.ok:
                err = r.json().get('error', f"Status code {r.status_code}")
                raise MatrixError(err)
                # print(f"[!] Error while making request to {endpoint}: {err}")
                # return None

            return r.json()
        except Exception as e:
            raise ParsingError(f"Error while parsing response: {e}")
            # print(f"[!] Error while parsing response: {e}")
            # print(r.text)
            # return None

    def login(self,
              start_syncing: bool = True,
              device_id: str = "") -> Authentication:
        """
        Login to the homeserver.

        :param start_syncing: Start the sync thread.
        :param device_id: The device id.
        :return: The authentication object.
        """
        data = {
            "type": "m.login.password",
            "user": self.user,
            "password": self.pwd
        }

        if device_id: data["device_id"] = device_id

        r = self._make_request("POST", "/login", data, skip_auth_check=True)
        if r:
            self.auth = Authentication(access_token=r["access_token"],
                                       user_id=r["user_id"],
                                       device_id=r["device_id"],
                                       home_server=r["home_server"])

            if start_syncing: self.start_sync()
            return self.auth

    def register(self, start_syncing: bool = True) -> Authentication:
        """
        Register a new user.

        :param start_syncing: Start the sync thread.
        :return: The authentication object.
        """
        data = {
            "username": self.user,
            "password": self.pwd,
            "auth": {
                "type": "m.login.dummy"
            }
        }
        r = self._make_request("POST", "/register", data, skip_auth_check=True)
        if r:
            self.auth = Authentication(access_token=r["access_token"],
                                       user_id=r["user_id"],
                                       device_id=r["device_id"],
                                       home_server=r["home_server"])

            if start_syncing: self.start_sync()
            return self.auth

    def start_sync(self) -> None:
        """Start the sync thread."""
        self.sync(set_as_new=True)
        threading.Thread(target=self.sync_thread).start()

    def sync_thread(self) -> None:
        """Sync thread."""
        while self.run:
            sleep(self.sync_delay)
            # self.sync(since=self.state.next_batch)
            self.sync(set_as_new=True)

    # https://github.com/matrix-org/matrix-python-sdk/blob/887f5d55e16518a0a2bef4f2d6bff6ecf48d18c1/matrix_client/api.py#L1085
    def _make_txn_id(self):
        txn_id = str(self.txn_id) + str(int(time() * 1000))
        self.txn_id += 1
        return txn_id

    def create_room(self,
                    alias: str = "",
                    preset: str = Room_Preset.public_chat,
                    topic: str = "",
                    invite: List[str] = [],
                    creation_content: Dict = {},
                    initial_state: List[Event] = [],
                    visibility: str = "private",
                    power_level_content_override: Dict = {}) -> str:
        """
        Create a new room.

        :param alias: Room alias
        :param preset: Room preset from classes.Room_Preset.
        :param topic: Room topic
        :param invite: List of user IDs to invite
        :param creation_content: Room creation content
        :param initial_state: Initial state
        :param visibility: Room visibility
        :param power_level_content_override: Override the default power levels.
        :return: Room ID
        """
        data = {}
        if alias: data = {"room_alias_name": alias}
        if preset: data["preset"] = preset
        if topic: data["topic"] = topic
        if invite: data["invite"] = invite
        if creation_content: data["creation_content"] = creation_content
        if initial_state: data["initial_state"] = initial_state
        if visibility: data["visibility"] = visibility
        if power_level_content_override:
            data["power_level_content_override"] = power_level_content_override

        res = self._make_request("POST", "/createRoom", data)
        return res.get("room_id")

    def create_space(self,
                     alias: str = "",
                     preset: str = Room_Preset.public_chat,
                     topic: str = "",
                     invite: List[str] = [],
                     creation_content: Dict = {"type": "m.space"},
                     initial_state: List[Event] = [],
                     visibility: str = "private",
                     power_level_content_override: Dict = {}) -> str:
        """
        Create a new space. Wrapper for create_room.

        :param alias: Alias for the room.
        :param preset: Room preset from classes.Room_Preset.
        :param topic: Room topic.
        :param invite: List of users to invite.
        :param creation_content: Room creation content.
        :param initial_state: Initial state for the room.
        :param visibility: Room visibility.
        :param power_level_content_override: Override the default power levels.
        :return: Room ID.
        """
        data = {}
        if preset: data["preset"] = preset
        if alias: data["alias"] = topic
        if topic: data["topic"] = topic
        if invite: data["invite"] = invite
        if creation_content: data["creation_content"] = creation_content
        if initial_state: data["initial_state"] = initial_state
        if visibility: data["visibility"] = visibility
        if power_level_content_override:
            data["power_level_content_override"] = power_level_content_override

        res = self._make_request("PUT", "/createRoom", data)
        return res.get("room_id")

    def invite_to_room(self, user_id: str, room_id: str) -> dict:
        """
        Invite a user to a room.
        :param user_id: The user id to invite.
        :param room_id: The room id to invite the user to.
        :return: The response from the homeserver.
        """
        data = {"user_id": user_id}
        return self._make_request("POST", f"/rooms/{room_id}/invite", data)

    def send_room_event(self,
                        room_id: str,
                        event_type: str,
                        content: Dict,
                        txn_id: int = None) -> dict:
        """
        Send arbitrary event to a room

        :param room_id: The room id to send the event to.
        :param event_type: The event type.
        :param content: The event content.
        :param state_key: The state key. (optional)
        :return: The response from the homeserver.
        """
        if not txn_id:
            txn_id = self._make_txn_id()

        path = f"/rooms/{quote(room_id)}/send/{quote(event_type)}/{quote(str(txn_id))}"
        return self._make_request("PUT", path, content)

    def send_message(self,
                     room_id: str,
                     message: str,
                     msgtype: str = "m.text",
                     format: str = "",
                     formatted_body: str = "",
                     url: str = "",
                     info: Dict = {}) -> Event:
        """
        Send a message to a room.

        :param room_id: Room ID
        :param message: Message text
        :param msgtype: Message type
        :param format: Message format
        :param formatted_body: Message formatted body
        :param url: URL, only for m.image, m.file, m.audio, m.video
        :param info: Additional info, only for m.image, m.file, m.audio, m.video: see https://matrix.org/docs/spec/r0.0.1/client_server.html
        :return: Event object
        """

        data = {"msgtype": msgtype, "body": message}
        if format: data["format"] = format
        if formatted_body: data["formatted_body"] = formatted_body
        if url: data["url"] = url
        if info: data["info"] = info

        res = self.send_room_event(room_id, "m.room.message", data)
        return Event(res["event_id"], timestamp=time())

    def leave_room(self, room_id: str) -> dict:
        """
        Leave a room.

        :param room_id: Room ID
        """
        return self._make_request("POST", f"/rooms/{room_id}/leave", {})

    def sync(self, since: str = "", set_as_new: bool = False) -> State:
        """
        Sync the client state.

        :param since: The token to sync from.
        :param set_as_new: Set the state as new.
        :return: The new state.
        """
        params = {}
        # if since: params["since"] = since
        # if self.set_as_online: params["presence"] = "online"

        res = self._make_request("GET", "/sync", {}, params=params)

        state = parse_state(res)
        self.state = state
        # if set_as_new:
        #     self.state = state
        # else:
        #     self.state.next_batch = state.next_batch
        #     self.state.invited_rooms += state.invited_rooms
        #     self.state.joined_rooms += state.joined_rooms

        return self.state

    def get_room_id(self, room_alias: str) -> str:
        """
        Get the room id from a room alias.

        :param room_alias: The room alias.
        :return: The room id.
        """
        content = self._make_request(
            "GET", "/directory/room/{}".format(quote(room_alias)))
        return content.get("room_id", None) if content else None

    def get_room_members(self, room_id: str) -> List[User]:
        """
        Get the members of a room.

        :param room_id: The room id.
        :return: List of users.
        """
        res = self._make_request("GET", f"/rooms/{room_id}/joined_members")
        if res:
            return [
                User(i, avatar_url=res["joined"][i]["avatar_url"])
                for i in res["joined"]
            ]
        return []

    def whoami(self) -> User:
        """
        Get the user info.

        :return: The user object.
        """
        res = self._make_request("GET", "/account/whoami")
        return User(res["user_id"], res["device_id"],
                    res["org.matrix.msc3069.is_guest"]) if res else None

    def join_room(self, room_id: str, reason: str = "") -> Event:
        """
        Join a room or space.

        :param room_id: The room id.
        :param reason: The reason for joining.
        :return: The event object.
        """
        data = {"reason": reason} if reason else {}
        res = self._make_request("POST", f"/rooms/{quote(room_id)}/join", data)
        if res:
            return res
        return None

    def forget_room(self, room_id: str) -> Event:
        """
        Forget a room.

        :param room_id: The room id to forget.
        :return: The event object.
        """
        res = self._make_request("POST", f"/rooms/{quote(room_id)}/forget", {})
        if res:
            return res
        return None

    def leave_room(self, room_id: str) -> Event:
        """
        Leave a room.

        :param room_id: The room id to leave.
        :return: The event object.
        """
        res = self._make_request("POST", f"/rooms/{quote(room_id)}/leave", {})
        if res:
            return res
        return None

    def get_room_events(
            self,
            room_id: str,
            direction: str = "b",
            limit: int = 10,
            only_events: List[str] = ["m.room.message", "m.room.member"
                                      ],  # only joins and messages
            to_t: str = "",
            from_t: str = "",
            filter: str = "") -> List[Event]:
        """
        Get the events of a room.

        :param room_id: The room id.
        :param direction: The direction of the events.
        :param limit: How many events to get.
        :param only_events: Only get events of these types.
        :param to_t: Get events before this timestamp.
        :param from_t: Get events after this timestamp.
        :param filter: Filter the events.
        :return: List of events.
        """

        params = {
            "from": from_t,
            "to": to_t,
            "limit": limit,
            "dir": direction,
            "filter": filter
        }
        res = self._make_request("GET",
                                 f"/rooms/{quote(room_id)}/messages",
                                 params=params)
        if res:
            if only_events:
                events = [
                    event for event in res["chunk"]
                    if event["type"] in only_events
                ]
            else:
                events = res["chunk"]

            return parse_room_events(events)

        return None

    def mark_as_read(self, room_id: str, event_id: str) -> dict:
        """
        Mark an event as read.

        :param room_id: The room id.
        :param event_id: The event id.
        :return: The response from the homeserver.
        """
        data = {"m.fully_read": event_id}
        return self._make_request("POST",
                                  f"/rooms/{quote(room_id)}/read_markers",
                                  data=data)

    def run_forever(self):
        """Run the client forever."""
        while self.run:
            sleep(1)

    def upload_keys(self, device_id: str, keys: str) -> dict:
        """
        Upload keys to the homeserver.
        https://matrix.org/docs/spec/client_server/r0.4.0#post-matrix-client-r0-keys-upload

        :param device_id: The device id
        :param keys: The keys to upload
        :return: The response from the homeserver.
        """
        data = {"device_id": device_id, "keys": keys}
        return self._make_request("POST", "/keys/upload", data=data)

    def query_keys(self,
                   device_keys: Mapping[str, List[str]],
                   timeout: int = 10000,
                   since: str = "") -> Device_Keys_Response:
        """
        Query keys from the homeserver.
        https://matrix.org/docs/spec/client_server/r0.4.0#post-matrix-client-r0-keys-query

        :param device_keys: The device keys to query.
        :param timeout: The timeout in milliseconds.
        :return: The response from the homeserver.
        """
        data = {"device_keys": device_keys, "timeout": timeout}
        if since: data["since"] = since

        res = self._make_request("POST", "/keys/query", data=data)
        if res:
            return parse_device_keys_response(res)
        return None

    def claim_keys(self,
                   keys: Mapping[str, Mapping[str, str]],
                   timeout: int = 10000) -> dict:
        """
        Claim keys from the homeserver.
        https://matrix.org/docs/spec/client_server/r0.4.0#post-matrix-client-r0-keys-claim

        :param keys: The keys to claim.
        :param timeout: The timeout in milliseconds.
        :return: The response from the homeserver.
        """
        data = {"device_keys": keys, "timeout": timeout}
        return self._make_request("POST", "/keys/claim", data=data)

    def keys_changes(self, from_token: str, to_token: str) -> dict:
        """
        Get the changes in keys.
        https://matrix.org/docs/spec/client_server/r0.4.0#get-matrix-client-r0-keys-changes

        :param from_token: The token to start from. Should be the next_batch field from a response to an earlier call to /sync
        :param to_token: The token to end at. Should be the next_batch field from a recent call to /sync
        :return: The response from the homeserver.
        """
        params = {"from": from_token, "to": to_token}
        return self._make_request("GET", "/keys/changes", params=params)

    def add_room_to_space(self,
                          space_id: str,
                          room_id: str,
                          via: List[str],
                          suggested: bool = False,
                          auto_join: bool = False) -> Event:
        """
        Add a room to a space.

        :param space_id: The space id
        :param room_id: The room id
        :param via: List of servers (["matrix.org", "matrix.example.org"])
        :param suggested: Whether the room is suggested
        :param auto_join: Whether the room should be auto joined
        :return: The event
        """

        data = {"via": via, "suggested": suggested, "auto_join": auto_join}

        res = self._make_request(
            "POST",
            f"/rooms/{quote(space_id)}/state/m.space.child/{quote(room_id)}")
        if res:
            return parse_event(res)
        return None

    def media_upload(self,
                     content: Any,
                     content_type: str,
                     filename: str = None) -> Dict:
        """
        Upload media to the homeserver.

        :param content: The content to upload.
        :param content_type: The content type
        :param filename: The filename
        :return: The response from the homeserver.
        """

        query_params = {}
        if filename: query_params['filename'] = filename
        headers = {'Content-Type': content_type}

        return self._make_request("POST",
                                  "/upload",
                                  raw_data=content,
                                  params=query_params,
                                  headers=headers,
                                  API_path="/_matrix/media/r0")
