# Matrix.py 

![](https://img.shields.io/pypi/pyversions/matrix-chat?style=for-the-badge)
![](https://img.shields.io/pypi/l/matrix-chat?style=for-the-badge)
![](https://img.shields.io/pypi/v/matrix-chat?style=for-the-badge)

Matrix.py is a matrix bot library, inspired by the [discord.py](https://github.com/Rapptz/discord.py) library by Rapptz.
It is still in early beta, so don't expect it to be running smoothly yet.

It aims to be a modern, easy to use, feature-rich and async ready API wrapper for the Matrix system written in Python.

The documentation can be found [here](https://matrixpy.readthedocs.io/en/latest/matrix.html), examples can be found in the `examples` folder.


## Installing

The package can be installed from pypi, via
```zsh
$ pip install matrix-chat
```

## Quick Example

```py
import matrix 

class MyClient(matrix.Client):
    def on_ready(self):
        print('Logged on as', self.user)

    def on_message(self, message: matrix.Message):
        # don't respond to ourselves
        if message.author == self.user:
            return

        print(f"[Room: {message.room.id}] {message.author}: {message.content}")

    def on_invite(self, invite: matrix.Invite):
        print(f"{invite.inviter} has invited you to join {invite.room_id}")

client = MyClient()
client.run(
    username='@bot:matrix.org',
    password='password',
    homeserver='https://matrix.org',
)
```

## Limitations

 - It is still in an early version - not tested enough
 - Matrix.py doesn't yet support e2ee - it wont join or respond in encrypted rooms.