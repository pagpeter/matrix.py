from dataclasses import dataclass
from typing import List
# https://discordpy.readthedocs.io/en/stable/api.html

# https://discordpy.readthedocs.io/en/stable/api.html#user
@dataclass
class User:
    """Class to keep user data."""
    name: str # username/user_id
    id: str # same as name 
    avatar: str # avatar_url
    display_name: str # displayname
    
# temp
class Message:
    pass

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

    async def send(self, content: str):
        """Send a message to the room."""
        raise NotImplementedError

    async def invite_user(self, user_id: str):
        """Invite a user to the room."""
        raise NotImplementedError

    async def kick_user(self, user_id: str):
        """Kick a user from the room."""
        raise NotImplementedError

    async def ban_user(self, user_id: str):
        """Ban a user from the room."""
        raise NotImplementedError

    async def unban_user(self, user_id: str):
        """Unban a user from the room."""
        raise NotImplementedError

    async def set_topic(self, topic: str):
        """Set the topic of the room."""
        raise NotImplementedError

    async def set_name(self, name: str):
        """Set the name of the room."""
        raise NotImplementedError

    async def set_icon(self, icon: str):
        """Set the icon of the room."""
        raise NotImplementedError

    async def get_messages(self, limit: int = 100) -> List[Message]:
        """Get the messages of the room."""
        raise NotImplementedError

    async def get_users(self) -> List[User]:
        """Get the users of the room."""
        raise NotImplementedError


# https://discordpy.readthedocs.io/en/stable/api.html#message
@dataclass
class Message:
    """Class to keep message data."""
    type: str # should be "m.text" most of the times
    author: User # should be the user who sent the message
    content: str # the actual message
    id: str # should be the same as the event_id
    room: Room # should be the room_id
    created_at: int # original timestamp
    edited_at: int # last edit time

    # reactions: dict # should be empty most of the times

    async def delete(self):
        """Delete the message."""
        raise NotImplementedError

    async def edit(self, content: str):
        """Edit the message."""
        raise NotImplementedError

    async def add_reaction(self, emoji: str):
        """Add a reaction to the message."""
        raise NotImplementedError
    
    async def remove_reaction(self, emoji: str, user_id: str):
        """Remove a reaction from the message."""
        raise NotImplementedError

    async def clear_reactions(self):
        """Clear all reactions from the message."""
        raise NotImplementedError

    async def clear_reaction(self, emoji: str):
        """Clears a specific reaction from the message."""
        raise NotImplementedError

    async def ack(self):
        """Acknowledge the message (mark as read)."""
        raise NotImplementedError

    async def reply(self, content: str):
        """Reply to the message."""
        raise NotImplementedError

# https://discordpy.readthedocs.io/en/stable/api.html#invite
@dataclass
class Invite:
    """Class to keep invite data"""
    room_id: str
    inviter: str
    created_at: int
    _invite_state: dict 

    async def accept(self, reason: str = None):
        """Accept the invite."""
        raise NotImplementedError
    
    async def delete(self, reason: str = None):
        """Delete the invite."""
        raise NotImplementedError
