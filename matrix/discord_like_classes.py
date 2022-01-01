from dataclasses import dataclass
from time import time
from typing import List
from .API import Bot
from .classes import Event
# https://discordpy.readthedocs.io/en/stable/api.html

# https://discordpy.readthedocs.io/en/stable/api.html#user
@dataclass
class User:
    """Class to keep user data."""
    name: str # username/user_id
    id: str # same as name 
    avatar: str # avatar_url
    display_name: str # displayname
    _bot: Bot = None
    

class Message: pass


# https://discordpy.readthedocs.io/en/stable/api.html#channel
@dataclass
class Room: 
    """
    Class to keep room data.

    Equivalent to discord.TextChannel
    """
    id: str
    topic: str
    last_message: Message 
    last_message_id: str 
    _bot: Bot = None

    async def send(self, content: str, msg_type: str = "m.text", formatted_body: str = None, format: str = None, info: dict = {}):
        """Send a message to the room."""
        return self._bot.send_message(self.id, content, formatted_body=formatted_body, format=format, msgtype=msg_type, info=info)

    async def invite_user(self, user_id: str):
        """Invite a user to the room."""
        return self._bot.invite_to_room(user_id, self.id)

    async def get_users(self) -> List[User]:
        """Get the users of the room."""
        return self._bot.get_room_members(self.id)

    async def kick_user(self, user_id: str):
        """Kick a user from the room. (Not implemented)"""
        raise NotImplementedError

    async def ban_user(self, user_id: str):
        """Ban a user from the room. (Not implemented)"""
        raise NotImplementedError

    async def unban_user(self, user_id: str):
        """Unban a user from the room. (Not implemented)"""
        raise NotImplementedError

    async def set_topic(self, topic: str):
        """Set the topic of the room. (Not implemented)"""
        raise NotImplementedError

    async def set_name(self, name: str):
        """Set the name of the room. (Not implemented)"""
        raise NotImplementedError

    async def set_icon(self, icon: str):
        """Set the icon of the room. (Not implemented)"""
        raise NotImplementedError

    async def get_messages(self, limit: int = 100) -> List[Message]:
        """Get the messages of the room. (Not implemented)"""
        raise NotImplementedError




# https://discordpy.readthedocs.io/en/stable/api.html#message
@dataclass
class Message:
    """Class to keep message data."""
    type: str # should be "m.text" most of the times
    author: User # should be the user who sent the message
    content: str # the actual message
    id: str # should be the same as the event_id
    room: Room # should be the room
    channel: Room # should be the room, same as room
    created_at: int # original timestamp
    edited_at: int # last edit time
    _bot: Bot = None

    # reactions: dict # should be empty most of the times

    async def delete(self):
        """Delete the message. (Not implemented)"""
        raise NotImplementedError

    async def edit(self, content: str) -> Message:
        """
        Edit the message. (Not implemented)
        
        :param content: The new content of the message.
        :return: The edited message.
        """
        raise NotImplementedError

    async def add_reaction(self, emoji: str) -> Message:
        """
        Add a reaction to the message. (Not implemented)
        
        :param emoji: The emoji to add.
        :return: The message with the reaction.
        """
        raise NotImplementedError
    
    async def remove_reaction(self, emoji: str, user_id: str) -> Message:
        """
        Remove a reaction from the message. (Not implemented)
        
        :param emoji: The emoji to remove.
        :param user_id: The user who added the reaction.
        :return: The message without the reaction.
        """
        raise NotImplementedError

    async def clear_reactions(self) -> Message:
        """
        Clear all reactions from the message. (Not implemented)
        
        :return: The message without any reactions.
        """
        raise NotImplementedError

    async def clear_reaction(self, emoji: str) -> Message:
        """
        Clears a specific reaction from the message. (Not implemented)
        
        :param emoji: The emoji to clear.
        :return: The message without the reaction.
        """
        raise NotImplementedError

    async def ack(self) -> Message:
        """
        Acknowledge the message (mark as read). (Not implemented)
        
        :return: The message.
        """
        raise NotImplementedError

    async def reply(self, content: str, include_reply_to: bool = True) -> Event:
        """
        Reply to the message.
        
        :param content: The content of the reply.
        :param include_reply_to: Whether to include the previous message.
        :return: The Event (Event ID and timestamp).
        """
        if include_reply_to:
            content = {
                "msgtype": "m.text",
                "body": f"> <{self.author}> {self.content}\n\n{content}",
                "format": "org.matrix.custom.html",
                "m.relates_to": {
                    "m.in_reply_to": {
                        "event_id": self.id
                    }
                },
                "formatted_body": f"""<mx-reply><blockquote>
                    <a href=\"https://matrix.to/#/{self.room.id}/{self.id}\">In reply to
                    </a><a href=\"https://matrix.to/#/{self.author}\">
                    {self.author}</a><br>{self.content}
                    </blockquote></mx-reply>{content}"""
            }
            res = self._bot.send_room_event(self.room.id, "m.room.message", content)
            return Event(event_id=res.get("event_id"), timestamp=time())
        else:
            return self._bot.send_message(self.room.id, content)

# https://discordpy.readthedocs.io/en/stable/api.html#invite
@dataclass
class Invite:
    """Class to keep invite data"""
    room_id: str
    inviter: str
    created_at: int
    _invite_state: dict 
    _bot: Bot = None

    async def accept(self, reason: str = "") -> Event:
        """
        Accept the invite.
        
        :param reason: The reason for accepting the invite.
        :return: The Event (Event ID and timestamp).
        """
        return self._bot.join_room(self.room_id, reason=reason)
    
    async def decline(self) -> Event:
        """
        Decline the invite.
        
        :return: The Event (Event ID and timestamp).
        """
        return self._bot.leave_room(self.room_id)
